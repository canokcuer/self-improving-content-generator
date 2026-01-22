"""Tests for Socratic brief module."""

import pytest

from content_assistant.generation.brief import (
    ContentBrief,
    Platform,
    ContentType,
    validate_brief,
    get_questions,
    get_platform_guidelines,
    BriefError,
    SOCRATIC_QUESTIONS,
)


class TestContentBrief:
    """Tests for ContentBrief dataclass."""

    def test_create_brief_with_required_fields(self):
        """Test creating brief with only required fields."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Help readers understand detox benefits",
            audience="Health-conscious professionals aged 30-45",
            pain_point="Feeling tired and sluggish despite healthy eating",
            unique_angle="TheLifeCo's holistic approach combines ancient wisdom with modern science",
            core_message="True detox happens at the cellular level",
            call_to_action="Comment below with your biggest health challenge",
        )

        assert brief.platform == Platform.INSTAGRAM
        assert brief.content_type == ContentType.POST
        assert brief.transformation == "Help readers understand detox benefits"
        assert brief.evidence is None
        assert brief.keywords == []

    def test_create_brief_with_all_fields(self):
        """Test creating brief with all optional fields."""
        brief = ContentBrief(
            platform=Platform.LINKEDIN,
            content_type=ContentType.ARTICLE,
            transformation="Shift perception of wellness retreats",
            audience="C-suite executives",
            pain_point="Burnout without time for recovery",
            unique_angle="ROI of wellness investment",
            core_message="Prevention is cheaper than cure",
            call_to_action="Book a discovery call",
            evidence="Harvard study on executive wellness",
            emotional_journey="Skeptical to curious to convinced",
            objections="Too expensive, no time",
            tone="Professional but warm",
            hook_style="statistic",
            keywords=["wellness ROI", "executive health"],
            constraints="No competitor mentions",
        )

        assert brief.evidence == "Harvard study on executive wellness"
        assert brief.keywords == ["wellness ROI", "executive health"]
        assert brief.constraints == "No competitor mentions"

    def test_brief_to_dict(self):
        """Test converting brief to dictionary."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.REEL,
            transformation="Inspire morning routine change",
            audience="Young professionals",
            pain_point="Groggy mornings",
            unique_angle="5-minute ritual",
            core_message="Morning sets the tone",
            call_to_action="Try it tomorrow",
        )

        data = brief.to_dict()

        assert data["platform"] == "instagram"
        assert data["content_type"] == "reel"
        assert data["transformation"] == "Inspire morning routine change"
        assert data["keywords"] == []

    def test_brief_from_dict(self):
        """Test creating brief from dictionary."""
        data = {
            "platform": "linkedin",
            "content_type": "post",
            "transformation": "Change perception",
            "audience": "Managers",
            "pain_point": "Stress",
            "unique_angle": "Our approach",
            "core_message": "Wellness matters",
            "call_to_action": "Learn more",
            "tone": "professional",
        }

        brief = ContentBrief.from_dict(data)

        assert brief.platform == Platform.LINKEDIN
        assert brief.content_type == ContentType.POST
        assert brief.tone == "professional"

    def test_brief_from_dict_invalid_platform(self):
        """Test that invalid platform raises error."""
        data = {
            "platform": "invalid_platform",
            "content_type": "post",
            "transformation": "Test",
            "audience": "Test",
            "pain_point": "Test",
            "unique_angle": "Test",
            "core_message": "Test",
            "call_to_action": "Test",
        }

        with pytest.raises(BriefError):
            ContentBrief.from_dict(data)

    def test_brief_to_prompt_context(self):
        """Test formatting brief for prompts."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Test transformation",
            audience="Test audience",
            pain_point="Test pain point",
            unique_angle="Test angle",
            core_message="Test message",
            call_to_action="Test CTA",
            keywords=["wellness", "detox"],
        )

        context = brief.to_prompt_context()

        assert "## Content Brief" in context
        assert "Instagram" in context
        assert "Test transformation" in context
        assert "wellness, detox" in context


class TestValidateBrief:
    """Tests for brief validation."""

    def test_valid_brief_returns_empty_list(self):
        """Test that valid brief has no errors."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Help readers understand the importance of mindful eating",
            audience="Health-conscious individuals looking to improve their relationship with food",
            pain_point="Struggling with emotional eating and mindless snacking",
            unique_angle="TheLifeCo combines psychology with nutrition science",
            core_message="Mindful eating transforms your relationship with food",
            call_to_action="Save this post for your next meal",
        )

        errors = validate_brief(brief)

        assert errors == []

    def test_empty_required_field_returns_error(self):
        """Test that empty required fields are caught."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="",  # Empty
            audience="Test audience description here",
            pain_point="Test pain point description here",
            unique_angle="Test unique angle description",
            core_message="Test core message content",
            call_to_action="Test call to action here",
        )

        errors = validate_brief(brief)

        assert any("transformation" in e for e in errors)

    def test_short_required_field_returns_error(self):
        """Test that too-short fields are caught."""
        brief = ContentBrief(
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            transformation="Short",  # Too short
            audience="Test audience description here",
            pain_point="Test pain point description here",
            unique_angle="Test unique angle description",
            core_message="Test core message content",
            call_to_action="Test call to action here",
        )

        errors = validate_brief(brief)

        assert any("transformation" in e and "10 characters" in e for e in errors)


class TestSocraticQuestions:
    """Tests for Socratic questions."""

    def test_get_questions_returns_all_13(self):
        """Test that all 13 questions are returned."""
        questions = get_questions()

        assert len(questions) == 13

    def test_questions_have_required_fields(self):
        """Test that each question has required fields."""
        questions = get_questions()

        for q in questions:
            assert "id" in q
            assert "question" in q
            assert "hint" in q
            assert "required" in q

    def test_required_questions_count(self):
        """Test correct number of required questions."""
        required = [q for q in SOCRATIC_QUESTIONS if q["required"]]

        assert len(required) == 6


class TestPlatformGuidelines:
    """Tests for platform guidelines."""

    def test_instagram_guidelines(self):
        """Test Instagram guidelines content."""
        guidelines = get_platform_guidelines(Platform.INSTAGRAM)

        assert "hook" in guidelines.lower()
        assert "hashtag" in guidelines.lower()

    def test_linkedin_guidelines(self):
        """Test LinkedIn guidelines content."""
        guidelines = get_platform_guidelines(Platform.LINKEDIN)

        assert "professional" in guidelines.lower()

    def test_all_platforms_have_guidelines(self):
        """Test that all platforms have guidelines."""
        for platform in Platform:
            guidelines = get_platform_guidelines(platform)
            assert guidelines  # Not empty
