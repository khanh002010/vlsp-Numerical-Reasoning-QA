"""One source-review context for new SFT data and both inference entry points."""
import json
from vinumqa.nlp_module.inference.semantic_validation import REVIEW_GUIDANCE, source_catalog

SOURCE_REVIEW_PROFILE = 'source-review-v1'


def reviewed_context(context, tables):
    return (context + '\n\n### Source review\n' + REVIEW_GUIDANCE +
            '\nTable binding catalog: ' + json.dumps(source_catalog(tables), ensure_ascii=False))


def apply_prompt_profile(context, tables, profile='legacy'):
    if profile == 'legacy':
        return context
    if profile == SOURCE_REVIEW_PROFILE:
        return reviewed_context(context, tables)
    raise ValueError(f'Unknown prompt profile: {profile}')
