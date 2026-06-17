"""Convenience service functions for common Moodle operations.

These functions are thin wrappers around MoodleClient.call_api and return the raw
Moodle response for the given webservice. They are intentionally minimal — adapt
as needed for your Moodle version and available webservices.
"""
from typing import Any, List


def get_courses(client) -> Any:
    """List courses. Uses 'core_course_get_courses'."""
    return client.call_api("core_course_get_courses", {})


def get_course_users(client, courseid: int) -> Any:
    """Get enrolled users for a course. Uses 'core_enrol_get_enrolled_users'."""
    return client.call_api("core_enrol_get_enrolled_users", {"courseid": courseid})


def get_assignments(client, courseids: List[int]) -> Any:
    """Get assignments for one or more courses. Uses 'mod_assign_get_assignments'.

    Pass courseids as a list of ints.
    """
    return client.call_api("mod_assign_get_assignments", {"courseids": courseids})


def get_grades(client, userid: int, courseid: int | None = None) -> Any:
    """Get grade items for a user. Uses 'gradereport_user_get_grade_items'.

    Note: Depending on your Moodle setup, different grade-report functions may be
    required. This is a reasonable starting point.
    """
    params = {"userid": userid}
    if courseid is not None:
        params["courseid"] = courseid
    return client.call_api("gradereport_user_get_grade_items", params)
