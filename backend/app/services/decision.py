"""Decision engine: risk score -> level / decision / post status. Thresholds are configurable."""
from ..config import settings


def decide(risk: int):
    if risk <= settings.SAFE_MAX:
        return "SAFE", "PUBLISH", "PUBLISHED"
    if risk <= settings.WARNING_MAX:
        return "WARNING", "PUBLISH_WITH_WARNING", "WARNING"
    if risk <= settings.REVIEW_MAX:
        return "REVIEW", "MODERATOR_REVIEW", "UNDER_REVIEW"
    return "HIGH_RISK", "BLOCK_AND_REVIEW", "BLOCKED"  # never auto-deleted; moderator decides


NOTIFY = {
    "PUBLISHED": ("POST_PUBLISHED", "Your post has been published."),
    "WARNING": ("POST_WARNING", "Your post was published with a warning label because it could not be fully verified."),
    "UNDER_REVIEW": ("POST_REVIEW", "Your post has been sent for moderator review."),
    "BLOCKED": ("POST_BLOCKED", "Your post was blocked because of a high misinformation risk and sent to a moderator."),
}
