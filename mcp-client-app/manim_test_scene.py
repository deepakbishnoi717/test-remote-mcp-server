from manim import *


class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        square = Square(color=GREEN)
        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.wait(0.5)
