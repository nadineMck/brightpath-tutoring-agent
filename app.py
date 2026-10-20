"""Gradio entry point for the BrightPath Tutoring chatbot."""

import gradio as gr

from brightpath_agent import BrightPathAgent


agent = BrightPathAgent()


def respond(message, history):
    return agent.chat(message, history)


demo = gr.ChatInterface(
    fn=respond,
    title="BrightPath Tutoring Assistant",
    description=(
        "Ask about mathematics, physics, programming, English, tutors, prices, "
        "schedules, or course recommendations. You can also request enrollment "
        "follow-up or leave feedback."
    ),
    examples=[
        "What mathematics support do you offer for Grade 11?",
        "Compare private and small-group university programming prices.",
        "I study first-year engineering and struggle with mechanics. What should I choose?",
        "I want to enroll in Python tutoring.",
        "I have a complaint about a missed lesson.",
    ],
)


if __name__ == "__main__":
    demo.launch()
