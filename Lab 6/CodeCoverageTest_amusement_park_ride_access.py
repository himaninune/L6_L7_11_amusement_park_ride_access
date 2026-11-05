import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def make_group(ride_type="family", patrons=None, is_open=True, fast_lane=False):
    return {
        "is_open": is_open,
        "ride_type": ride_type,
        "has_fast_lane": fast_lane,
        "patrons": patrons if patrons is not None else [],
    }


def adult(height=170):
    return {"height_cm": height, "health_warning": False, "is_child": False}


def child(height=130):
    return {"height_cm": height, "health_warning": False, "is_child": True}


def test_single_adult_family_ride():
    result = process_ride_admissions([make_group(patrons=[adult(150)])], 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


def test_invalid_groups_type():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_closed_group_skipped():
    result = process_ride_admissions([make_group(patrons=[adult()], is_open=False)], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_roller_coaster_adult_and_child_with_fast_lane():
    group = make_group("roller_coaster", [adult(), child()], fast_lane=True)
    result = process_ride_admissions([group], 5.0)
    assert result["total_revenue"] == 25.0 + 15.0 + 5.0
    assert result["status"] == "COMPLETED"


def test_invalid_height_rejected():
    result = process_ride_admissions([make_group(patrons=[adult(0)])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_on_roller_coaster_breaks_group():
    sick = {"height_cm": 170, "health_warning": True, "is_child": False}
    group = make_group("roller_coaster", [adult(), sick, adult()])
    result = process_ride_admissions([group], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_too_short_rejected():
    result = process_ride_admissions([make_group(patrons=[adult(100), adult()])], 5.0)
    assert result["total_revenue"] == 10.0


def test_safety_audit_after_many_rejections():
    patrons = [adult(100)] * 5
    result = process_ride_admissions([make_group(patrons=patrons)], 5.0)
    assert result["status"] == "SAFETY_AUDIT"


def test_restraints_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraints_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"
