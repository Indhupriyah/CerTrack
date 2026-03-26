"""
Career Strategy Engine - rule-based only (no OpenAI).
Computes: gap analysis, deadline risk, failure patterns, effort vs outcome, productivity score.
"""
from datetime import date, timedelta
from collections import defaultdict


def _parse_skills(text):
    """Parse comma-separated skills into normalized set."""
    if not text or not text.strip():
        return set()
    return {s.strip().lower() for s in text.split(",") if s.strip()}


def get_user_acquired_skills(certifications, events):
    """From completed certs and event participation, derive acquired skills."""
    skills = set()
    for c in certifications:
        if c.skill_tags:
            skills.update(_parse_skills(c.skill_tags))
    for e in events:
        if e.event_type:
            skills.add(e.event_type.lower().replace(" ", "_"))
    return skills


def career_gap_analysis(role, user_acquired_skills):
    """
    role: CareerRole or dict with name, required_skills, recommended_cert_keywords.
    Returns: required_skills (list), acquired (list), missing (list), recommended_keywords (list).
    """
    required = _parse_skills(role.required_skills if hasattr(role, "required_skills") else role.get("required_skills", ""))
    acquired = required & user_acquired_skills
    missing = required - user_acquired_skills
    rec = (role.recommended_cert_keywords or role.get("recommended_cert_keywords") or "")
    recommended_keywords = [k.strip() for k in rec.split(",") if k.strip()]
    return {
        "required_skills": sorted(required),
        "acquired_skills": sorted(acquired),
        "missing_skills": sorted(missing),
        "recommended_keywords": recommended_keywords,
    }


def deadline_risk_predictor(active_certifications, completed_certifications, today):
    """
    For each active cert: compare days_left vs avg_days_to_complete (from past).
    Risk: high if days_left < avg_days_to_complete, else low/medium.
    """
    # Average days from registration/start to completion (from completed certs)
    completion_days = []
    for c in completed_certifications:
        start = c.registration_deadline or c.expected_completion or (c.completed_date - timedelta(days=60))
        if c.completed_date and start:
            completion_days.append((c.completed_date - start).days)
    avg_days = sum(completion_days) / len(completion_days) if completion_days else 30

    risks = []
    for c in active_certifications:
        deadline = c.expected_completion or c.registration_deadline
        if not deadline:
            continue
        days_left = (deadline - today).days
        if days_left < 0:
            risk = "overdue"
        elif days_left < avg_days * 0.5:
            risk = "high"
        elif days_left < avg_days:
            risk = "medium"
        else:
            risk = "low"
        risks.append({
            "cert_id": c.id,
            "name": c.name,
            "deadline": deadline,
            "days_left": days_left,
            "avg_days_typical": int(avg_days),
            "risk": risk,
        })
    return {"avg_completion_days": int(avg_days), "items": risks}


def failure_pattern_analyzer(events):
    """Aggregate event outcomes: rounds cleared, rejections, wins."""
    by_status = defaultdict(int)
    for e in events:
        s = (e.result_status or "unknown").strip() or "unknown"
        by_status[s] += 1
    total = len(events)
    return {
        "by_status": dict(by_status),
        "total_events": total,
        "win_rate": round(100 * by_status.get("winner", 0) / total, 1) if total else 0,
        "participation_rate": round(100 * (total - by_status.get("not_selected", 0)) / total, 1) if total else 0,
    }


def effort_vs_outcome_analysis(analytics_rows, completed_certs_count, events_win_count):
    """
    Correlate study_minutes and login/activity with outcomes.
    Returns simple ratios and trend hint.
    """
    total_study = sum((r.study_minutes or 0) for r in analytics_rows)
    total_logins = sum((r.login_count or 0) for r in analytics_rows)
    return {
        "total_study_minutes": total_study,
        "total_logins": total_logins,
        "completed_certs": completed_certs_count,
        "event_wins": events_win_count,
        "study_per_cert": round(total_study / completed_certs_count, 1) if completed_certs_count else 0,
        "hint": "Increase study time for more completions" if completed_certs_count and total_study / max(completed_certs_count, 1) < 60 else "Keep consistent effort",
    }


def productivity_score(certs_completed, certs_missed, events_participated, deadlines_met, deadlines_missed):
    """
    Simple weighted score 0–100.
    Weights: completions +, participated +, deadlines_met +, missed -.
    """
    score = 0.0
    score += min(certs_completed * 8, 40)
    score += min(events_participated * 3, 20)
    score += min(deadlines_met * 2, 20)
    score -= min(certs_missed * 5, 25)
    score -= min(deadlines_missed * 3, 25)
    return max(0, min(100, int(score)))


def certification_path_mapping(completed_certifications, templates_by_category):
    """
    Build a simple "path": group completed by skill/category, suggest next from templates.
    templates_by_category: dict category -> list of CertificationTemplate.
    """
    by_category = defaultdict(list)
    for c in completed_certifications:
        tags = (c.skill_tags or "").split(",")
        for t in tags:
            cat = t.strip() or "General"
            by_category[cat].append(c.name)
    suggested = []
    for cat, template_list in (templates_by_category or {}).items():
        completed_in_cat = set(by_category.get(cat, []))
        for t in (template_list or [])[:3]:
            if t.name not in completed_in_cat:
                suggested.append({"category": cat, "name": t.name, "platform": getattr(t, "platform", "")})
    return {"by_category": dict(by_category), "suggested_next": suggested[:10]}


def career_readiness_score(
    certs_completed,
    certs_total,
    events_participated,
    skill_count,
    last_activity_days_ago,
    productivity_score_value,
    deadlines_met,
    deadlines_missed,
):
    """
    Career Readiness Score 0–100 for placement: certifications, events, skill diversity, activity consistency.
    """
    score = 0.0
    # Certification achievement (up to 30)
    if certs_total > 0:
        score += 30 * (certs_completed / max(certs_total, 1))
    else:
        score += min(certs_completed * 6, 30)
    # Event participation (up to 25)
    score += min(events_participated * 5, 25)
    # Skill diversity (up to 20)
    score += min(skill_count * 2, 20)
    # Activity consistency: recent activity boosts (up to 15)
    if last_activity_days_ago is not None:
        if last_activity_days_ago <= 7:
            score += 15
        elif last_activity_days_ago <= 30:
            score += 10
        elif last_activity_days_ago <= 90:
            score += 5
    else:
        score += 5
    # Productivity component (up to 10)
    score += (productivity_score_value or 0) / 10
    # Deadline discipline: small penalty for missed
    score -= min(deadlines_missed * 2, 10)
    return max(0, min(100, int(score)))
