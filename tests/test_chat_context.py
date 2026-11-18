"""Regresie výberu kontextu podľa návrhu Claude chatu EOS, §5.3–5.6."""

import unittest

from scripts.ai.context import ContextText, Message, Source, Summary, Turn, prepare_context


class ChatContextTests(unittest.TestCase):
    def test_recent_turns_keep_order_and_do_not_overlap_summary(self):
        turns = [Turn(1, "prvá", "odpoveď"), Turn(2, "druhá", "odpoveď")]
        summary = Summary(1, ContextText("Dohodnutý formát."))
        context = prepare_context("pokračuj", turns, can_use_source=lambda source: True,
                                  summary=summary, max_turns=1)

        self.assertEqual(context.messages, (Message("user", "druhá"),
                                           Message("assistant", "odpoveď"),
                                           Message("user", "pokračuj")))
        self.assertEqual(context.summary, summary.content)
        overlapping = prepare_context("pokračuj", turns, can_use_source=lambda source: True,
                                      summary=summary)
        self.assertIsNone(overlapping.summary)

    def test_revoked_or_outdated_sources_remove_entire_blocks(self):
        current = Source("example", "2")
        outdated = Source("example", "1")
        revoked = Source("other-example", "1")
        allowed_memory = ContextText("Použi potvrdený formát.", (current,))
        private_memory = ContextText("Dôverný príklad.", (revoked,))
        context = prepare_context(
            "pokračuj", [Turn(2, "interná otázka", "interná odpoveď", (current, revoked)),
                         Turn(3, "bežná otázka", "bežná odpoveď", (current,))],
            can_use_source=lambda source: source == current,
            summary=Summary(1, ContextText("Staršia revízia.", (outdated,))),
            approved_memories=(private_memory, allowed_memory),
        )

        self.assertEqual(context.messages, (Message("user", "bežná otázka"),
                                           Message("assistant", "bežná odpoveď"),
                                           Message("user", "pokračuj")))
        self.assertIsNone(context.summary)
        self.assertEqual(context.memories, (allowed_memory,))

    def test_utf8_budget_preserves_question_and_complete_turns(self):
        context = prepare_context(
            "ž", [Turn(1, "a", "b"), Turn(2, "e", "č")], can_use_source=lambda source: True,
            approved_memories=(ContextText("é"), ContextText("a")), max_bytes=6,
        )

        self.assertEqual(context.messages, (Message("user", "e"), Message("assistant", "č"),
                                           Message("user", "ž")))
        self.assertEqual(context.memories, (ContextText("a"),))
        with self.assertRaisesRegex(ValueError, "exceeds"):
            prepare_context("ž", (), can_use_source=lambda source: True, max_bytes=1)
