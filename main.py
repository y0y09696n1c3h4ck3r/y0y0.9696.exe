from __future__ import annotations

import random
import time
import turtle
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
AVATAR_PATH = BASE_DIR / "avatar.png"

screen = turtle.Screen()
screen.title("AI Virtual Pet — avatar foto 1")
screen.bgcolor("lightblue")
screen.setup(width=700, height=650)
screen.tracer(False)

# Turtle accepts GIF shapes. The companion script creates avatar.gif from IMG_0065.JPG.
pet = turtle.Turtle()
pet.penup()
pet.goto(0, -20)
if AVATAR_PATH.exists():
    screen.addshape(str(AVATAR_PATH))
    pet.shape(str(AVATAR_PATH))
else:
    pet.shape("circle")
    pet.shapesize(5)
    pet.color("green")

status_display = turtle.Turtle(visible=False)
status_display.penup()
status_display.goto(-320, 250)

help_display = turtle.Turtle(visible=False)
help_display.penup()
help_display.goto(-320, -290)
help_display.write("F = alimentar    P = brincar    S = dormir    Q = sair",
                    font=("Arial", 12, "normal"))

stats = {"hunger": 20, "boredom": 20, "energy": 80}
last_tick = time.monotonic()
closed = False


def clamp(value: int) -> int:
    return max(0, min(100, int(value)))


def update_status() -> None:
    status_display.clear()
    if stats["hunger"] > 70:
        mood = "Faminto!"
    elif stats["boredom"] > 70:
        mood = "Entediado..."
    elif stats["energy"] < 30:
        mood = "Com sono..."
    else:
        mood = "Feliz!"

    text = (
        f"Humor: {mood}\n"
        f"Fome: {stats['hunger']}/100\n"
        f"Tédio: {stats['boredom']}/100\n"
        f"Energia: {stats['energy']}/100"
    )
    status_display.write(text, font=("Arial", 14, "bold"))
    screen.update()


def animate_jump(step: int = 0) -> None:
    if closed or step >= 4:
        pet.goto(0, -20)
        screen.update()
        return
    pet.goto(0, 35 if step % 2 == 0 else -20)
    screen.update()
    screen.ontimer(lambda: animate_jump(step + 1), 120)


def feed() -> None:
    stats["hunger"] = clamp(stats["hunger"] - 30)
    update_status()


def play() -> None:
    if stats["energy"] <= 20:
        update_status()
        return
    stats["boredom"] = clamp(stats["boredom"] - 40)
    stats["energy"] = clamp(stats["energy"] - 20)
    stats["hunger"] = clamp(stats["hunger"] + 10)
    update_status()
    animate_jump()


def sleep() -> None:
    stats["energy"] = clamp(stats["energy"] + 50)
    stats["hunger"] = clamp(stats["hunger"] + 15)
    update_status()


def tick() -> None:
    global last_tick
    if closed:
        return
    now = time.monotonic()
    if now - last_tick >= 5:
        stats["hunger"] = clamp(stats["hunger"] + 5)
        stats["boredom"] = clamp(stats["boredom"] + 5)
        stats["energy"] = clamp(stats["energy"] - 2)
        last_tick = now
        if stats["energy"] > 30:
            pet.goto(random.randint(-100, 100), random.randint(-100, 80))
        update_status()
    screen.ontimer(tick, 100)


def quit_game() -> None:
    global closed
    closed = True
    screen.bye()


screen.listen()
screen.onkey(feed, "f")
screen.onkey(play, "p")
screen.onkey(sleep, "s")
screen.onkey(quit_game, "q")
screen.getcanvas().winfo_toplevel().protocol("WM_DELETE_WINDOW", quit_game)
update_status()
tick()

try:
    screen.mainloop()
except turtle.Terminator:
    pass


def prepare_avatar(source: Path, destination: Path) -> None:
    """Create a cropped GIF with the white background made transparent."""
    from PIL import Image

    image = Image.open(source).convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, _ = pixels[x, y]
            if r > 245 and g > 245 and b > 245:
                pixels[x, y] = (255, 255, 255, 0)
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    image.thumbnail((260, 220), Image.Resampling.LANCZOS)
    image.save(destination, "GIF", transparency=0)


if __name__ == "__main__" and not AVATAR_PATH.exists():
    source = BASE_DIR / "IMG_0065.JPG"
    if source.exists():
        prepare_avatar(source, AVATAR_PATH)
        print(f"Avatar criado em: {AVATAR_PATH}")
        print("Execute novamente o programa para abrir o pet com o avatar.")
