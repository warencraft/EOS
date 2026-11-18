"""Local selection of the context for the EOS chat.

Call this after authorizing the chat and current question. Supply only completed
turns owned by that chat in chronological order, and only approved memories
already scoped to the caller and ranked by relevance. Sources include all records
on which a text depends, including those inherited from earlier turns.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Source:
    record_id: str
    revision: str


@dataclass(frozen=True)
class ContextText:
    text: str
    sources: tuple[Source, ...] = ()


@dataclass(frozen=True)
class Turn:
    number: int
    question: str
    answer: str
    sources: tuple[Source, ...] = ()


@dataclass(frozen=True)
class Summary:
    through_turn: int
    content: ContextText


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class ChatContext:
    messages: tuple[Message, ...]
    summary: ContextText | None
    memories: tuple[ContextText, ...]


def prepare_context(
    question: str,
    turns: Sequence[Turn],
    *,
    can_use_source: Callable[[Source], bool],
    summary: Summary | None = None,
    approved_memories: Sequence[ContextText] = (),
    max_bytes: int = 12_000,
    max_turns: int = 5,
    max_memories: int = 3,
) -> ChatContext:
    """Bound dynamic text by UTF-8 bytes, excluding provider framing and metadata.

    The source callback must verify current access, AI consent and the exact
    revision. The caller passes returned memories and summary as reference data.
    """
    if not question.strip():
        raise ValueError("Question must not be empty.")
    if max_bytes < 1 or max_turns < 0 or max_memories < 0:
        raise ValueError("Context limits are out of range.")

    remaining = max_bytes - len(question.encode("utf-8"))
    if remaining < 0:
        raise ValueError("Question exceeds the context budget.")

    selected_turns: list[Turn] = []
    for turn in reversed(turns[max(0, len(turns) - max_turns):]):
        if not all(can_use_source(source) for source in turn.sources):
            continue
        size = len(turn.question.encode("utf-8")) + len(turn.answer.encode("utf-8"))
        if size > remaining:
            break
        selected_turns.append(turn)
        remaining -= size

    selected_summary = None
    if summary is not None:
        overlaps = selected_turns and summary.through_turn >= selected_turns[-1].number
        size = len(summary.content.text.encode("utf-8"))
        if not overlaps and size <= remaining:
            if all(can_use_source(source) for source in summary.content.sources):
                selected_summary = summary.content
                remaining -= size

    selected_memories: list[ContextText] = []
    for memory in approved_memories:
        if len(selected_memories) == max_memories:
            break
        size = len(memory.text.encode("utf-8"))
        if size <= remaining and all(can_use_source(source) for source in memory.sources):
            selected_memories.append(memory)
            remaining -= size

    messages: list[Message] = []
    for turn in reversed(selected_turns):
        messages.extend((Message("user", turn.question), Message("assistant", turn.answer)))
    messages.append(Message("user", question))
    return ChatContext(tuple(messages), selected_summary, tuple(selected_memories))
