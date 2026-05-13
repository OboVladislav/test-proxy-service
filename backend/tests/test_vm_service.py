import bcrypt
import pytest

from app.models.vm import VirtualMachine
from app.models.user import User
from app.services.vm_service import get_free_vm, assign_vm_to_user


def make_user(db, email="u@test.com"):
    user = User(
        email=email,
        password=bcrypt.hashpw(b"pass", bcrypt.gensalt()).decode(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_vm(db, name="p1", user_id=None):
    vm = VirtualMachine(
        name=name, host="10.0.0.1", port=1080,
        protocol="socks5", current_user_id=user_id,
    )
    db.add(vm)
    db.commit()
    db.refresh(vm)
    return vm


def test_get_free_vm_returns_free_vm(db):
    make_vm(db)
    result = get_free_vm(db)
    assert result is not None
    assert result.current_user_id is None


def test_get_free_vm_returns_none_when_all_busy(db):
    user = make_user(db)
    make_vm(db, user_id=user.id)
    assert get_free_vm(db) is None


def test_get_free_vm_skips_inactive(db):
    vm = make_vm(db)
    vm.is_active = False
    db.commit()
    assert get_free_vm(db) is None


def test_get_free_vm_returns_first_free_among_many(db):
    user = make_user(db)
    make_vm(db, name="busy", user_id=user.id)
    free = make_vm(db, name="free")

    result = get_free_vm(db)
    assert result.id == free.id


def test_assign_vm_sets_user_id(db):
    user = make_user(db)
    vm = make_vm(db)

    assign_vm_to_user(db, vm, user.id)
    db.refresh(vm)

    assert vm.current_user_id == user.id


def test_assign_vm_sets_last_used_at(db):
    user = make_user(db)
    vm = make_vm(db)

    assign_vm_to_user(db, vm, user.id)
    db.refresh(vm)

    assert vm.last_used_at is not None


def test_assign_vm_makes_no_free_vm(db):
    user = make_user(db)
    vm = make_vm(db)

    assign_vm_to_user(db, vm, user.id)

    assert get_free_vm(db) is None
