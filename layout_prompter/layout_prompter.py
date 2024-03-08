from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

from layout_prompter.modules import (
    LLM,
    ExemplarSelector,
    Ranker,
    RankerOutput,
    Serializer,
)

if TYPE_CHECKING:
    from layout_prompter.typehint import LayoutData

logger = logging.getLogger(__name__)


@dataclass
class LayoutPrompter(object):
    serializer: Serializer
    selector: ExemplarSelector
    llm: LLM
    ranker: Ranker

    def _generate_layout(
        self, prompt_messages: List[Dict[str, str]]
    ) -> List[RankerOutput]:
        response = self.llm(prompt_messages)
        return self.ranker(response)

    def generate_layout(
        self, prompt_messages: List[Dict[str, str]], max_num_try: int = 5
    ) -> List[RankerOutput]:
        for num_try in range(max_num_try):
            try:
                return self._generate_layout(prompt_messages)
            except Exception as err:
                logger.warning(f"#try {num_try}: {err}")

        raise ValueError(f"Failed to generate layout for prompt: {prompt_messages}")

    def __call__(self, layout_data: LayoutData, max_num_try: int = 5) -> Any:
        exemplars = self.selector(layout_data)
        prompt = self.serializer.build_prompt(
            exemplars=exemplars, layout_data=layout_data
        )
        prompt_messages = [
            {"role": "system", "content": prompt["system_prompt"]},
            {"role": "user", "content": prompt["user_prompt"]},
        ]
        return self.generate_layout(prompt_messages, max_num_try=max_num_try)
