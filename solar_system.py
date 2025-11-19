import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12
import os

# ------------------------
# تنظیمات کلی
# ------------------------
WIDTH, HEIGHT = 1280, 720  # اگر خواستی 1920x1080 هم می‌تونی بذاری


# ------------------------
# لود تکسچر اختیاری (JPG/PNG)
# ------------------------
def load_texture_optional(filename):
    if not os.path.exists(filename):
        print(f"[INFO] Texture not found: {filename}")
        return None

    surface = pygame.image.load(filename).convert_alpha()
    width, height = surface.get_size()

    has_alpha = surface.get_bitsize() == 32
    mode = "RGBA" if has_alpha else "RGB"
    gl_format = GL_RGBA if has_alpha else GL_RGB

    image_data = pygame.image.tostring(surface, mode, True)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexImage2D(GL_TEXTURE_2D, 0, gl_format, width, height, 0,
                 gl_format, GL_UNSIGNED_BYTE, image_data)

    return tex_id


def load_planet_textures(planet_names):
    textures = []
    for name in planet_names:
        base = name.lower()
        tex = load_texture_optional(base + ".jpg")
        if tex is None:
            tex = load_texture_optional(base + ".png")
        textures.append(tex)
    return textures


# ------------------------
# رسم کره رنگی با نور (Material)
# ------------------------
def draw_colored_sphere(color, radius, slices=80, stacks=80):
    glDisable(GL_TEXTURE_2D)
    glColor3f(*color)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)


# ------------------------
# رسم کره تکسچردار
# ------------------------
def draw_textured_sphere(tex_id, radius, slices=80, stacks=80):
    if tex_id is None:
        draw_colored_sphere((1.0, 1.0, 1.0), radius, slices, stacks)
        return

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(1.0, 1.0, 1.0)
    quad = gluNewQuadric()
    gluQuadricTexture(quad, GL_TRUE)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)
    glDisable(GL_TEXTURE_2D)


# ------------------------
# مدار
# ------------------------
def draw_orbit(radius):
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor3f(0.35, 0.35, 0.35)
    glBegin(GL_LINE_LOOP)
    for i in range(240):
        t = 2 * math.pi * i / 240
        x = math.cos(t) * radius
        z = math.sin(t) * radius
        glVertex3f(x, 0.0, z)
    glEnd()
    glEnable(GL_LIGHTING)


# ------------------------
# ستاره‌های پس‌زمینه
# ------------------------
def generate_stars(n=1000, spread=500):
    stars = []
    for _ in range(n):
        stars.append((
            random.uniform(-spread, spread),
            random.uniform(-spread, spread),
            random.uniform(-spread, spread),
        ))
    return stars


def draw_stars(stars, brightness=1.0):
    glDisable(GL_LIGHTING)
    glPointSize(1.5)
    glBegin(GL_POINTS)
    glColor3f(brightness, brightness, brightness)
    for x, y, z in stars:
        glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)


# ------------------------
# حلقه‌ی زحل
# ------------------------
def draw_saturn_ring(inner_radius, outer_radius):
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor4f(0.9, 0.8, 0.6, 0.7)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(0, 361):
        a = math.radians(i)
        x_in = math.cos(a) * inner_radius
        z_in = math.sin(a) * inner_radius
        x_out = math.cos(a) * outer_radius
        z_out = math.sin(a) * outer_radius
        glVertex3f(x_out, 0.0, z_out)
        glVertex3f(x_in, 0.0, z_in)
    glEnd()

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


# ------------------------
# نمایش متن سه‌بعدی روی صحنه (Label روی سیاره)
# ------------------------
def draw_3d_label(text, x, y, z, brightness=1.0):
    glDisable(GL_LIGHTING)
    glColor3f(brightness, brightness, brightness)
    glRasterPos3f(x, y, z)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glEnable(GL_LIGHTING)


# ------------------------
# main
# ------------------------
def main():
    pygame.init()
    glutInit()
    pygame.font.init()

    # فونت برای پنل اطلاعات
    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    info_font = pygame.font.SysFont("Arial", 18)

    # دیکشنری اطلاعات علمی مختصر برای هر سیاره
    planet_info = {
        "Mercury": [
            "Smallest planet in the Solar System",
            "Year length: 88 Earth days",
            "No real atmosphere, huge temp swings",
        ],
        "Venus": [
            "Hottest planet due to thick CO2 atmosphere",
            "Day is longer than its year",
            "Surface hidden under dense clouds",
        ],
        "Earth": [
            "Only known planet with life",
            "71% of surface covered by water",
            "Has one natural satellite: the Moon",
        ],
        "Mars": [
            "Known as the Red Planet",
            "Has the largest volcano: Olympus Mons",
            "Thin CO2 atmosphere, polar ice caps",
        ],
        "Jupiter": [
            "Largest planet, a gas giant",
            "Famous Great Red Spot storm",
            "Strong magnetic field and many moons",
        ],
        "Saturn": [
            "Famous for its bright ring system",
            "Gas giant with low density",
            "More than 80 known moons",
        ],
        "Uranus": [
            "Ice giant with a tilted rotation axis",
            "Rotates on its side",
            "Very cold, distant from the Sun",
        ],
        "Neptune": [
            "Farthest major planet from the Sun",
            "Strong winds and active weather",
            "Deep blue color from methane",
        ],
        "Pluto": [
            "Dwarf planet in the Kuiper Belt",
            "Highly elliptical orbit",
            "Thin atmosphere that freezes and falls as it moves away",
        ],
    }

    # آنتی‌الیاسینگ
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Cinematic 3D Solar System – Focus with Text & Textures + Moon + Intro")

    # Projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, WIDTH / HEIGHT, 1.0, 2000.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    # نور
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.10, 0.10, 0.10, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (0.95, 0.95, 0.95, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)

    stars = generate_stars()

    # name, distance, radius, orbit_speed, color
    planets = [
        ("Mercury",  14,  1.0, 0.80,  (0.8, 0.7, 0.5)),
        ("Venus",    18,  1.5, 0.55,  (1.0, 0.9, 0.6)),
        ("Earth",    22,  1.8, 0.48,  (0.3, 0.6, 1.0)),
        ("Mars",     26,  1.4, 0.42,  (1.0, 0.35, 0.25)),
        ("Jupiter",  35,  4.0, 0.26,  (1.0, 0.9, 0.75)),
        ("Saturn",   44,  3.4, 0.22,  (1.0, 0.92, 0.7)),
        ("Uranus",   52,  2.5, 0.16,  (0.7, 0.95, 1.0)),
        ("Neptune",  60,  2.5, 0.13,  (0.5, 0.6, 1.0)),
        ("Pluto",    68,  1.0, 0.10,  (0.85, 0.85, 0.9)),
    ]

    inclinations = [0.0, 3.0, -2.0, 1.5, -1.0, 0.5, -2.5, 1.0, 4.0]

    planet_names = [p[0] for p in planets]
    planet_textures = load_planet_textures(planet_names)

    angles = [0.0] * len(planets)
    planet_positions = [(0.0, 0.0, 0.0)] * len(planets)

    sun_rotation = 0.0

    camera_angle_global = 0.0
    camera_radius = 180.0
    camera_base_height = 80.0
    camera_speed_global = 0.20

    camera_focus_angle = 0.0
    camera_radius_focus = 40.0
    camera_height_focus = 20.0
    camera_speed_focus = 0.06

    paused = False
    focus_mode = False
    focus_target = 2  # Earth پیش‌فرض (کلید ۳)

    clock = pygame.time.Clock()
    running = True

    while running:
        # زمان بر حسب ثانیه
        t = pygame.time.get_ticks() / 1000.0

        # --- Intro fade-in در 2 ثانیه اول ---
        intro_factor = min(1.0, t / 2.0)

        # --- پس‌زمینه با نوسان ملایم ---
        bg = 0.02 + 0.01 * math.sin(t * 0.2)
        glClearColor(0.0, 0.0, bg, 1.0)

        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False
                if e.key == K_SPACE:
                    paused = not paused
                if e.key == K_f:
                    focus_mode = not focus_mode
                # انتخاب سیاره‌ی فوکوس: 1..9 → Mercury..Pluto
                if K_1 <= e.key <= K_9:
                    idx = e.key - K_1
                    if idx < len(planets):
                        focus_target = idx

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # دوربین
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if focus_mode:
            fx, fy, fz = planet_positions[focus_target]
            cam_focus_rad = math.radians(camera_focus_angle)
            cam_x = fx + math.cos(cam_focus_rad) * camera_radius_focus
            cam_z = fz + math.sin(cam_focus_rad) * camera_radius_focus
            cam_y = fy + camera_height_focus
            gluLookAt(cam_x, cam_y, cam_z,
                      fx, fy, fz,
                      0.0, 1.0, 0.0)
        else:
            camera_height = camera_base_height + 15.0 * math.sin(t * 0.3)
            cam_rad = math.radians(camera_angle_global)
            cam_x = math.cos(cam_rad) * camera_radius
            cam_z = math.sin(cam_rad) * camera_radius
            cam_y = camera_height
            gluLookAt(cam_x, cam_y, cam_z,
                      0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0)

        glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 0.0, 0.0, 1.0))

        # ستاره‌ها با روشنایی وابسته به intro
        draw_stars(stars, brightness=intro_factor)

        # ---------- خورشید ----------
        glPushMatrix()
        base_sun_color = (1.0, 0.9, 0.3)
        sun_color = tuple(c * intro_factor for c in base_sun_color)
        glColor3f(*sun_color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION,
                     (0.9 * intro_factor, 0.8 * intro_factor, 0.3 * intro_factor, 1.0))

        glRotatef(sun_rotation, 0, 1, 0)
        draw_colored_sphere(sun_color, radius=5.0, slices=100, stacks=100)

        # هاله‌ی خورشید
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 0.9, 0.4, 0.25 * intro_factor)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, 0.0, 0.0)
        R = 11.0
        for i in range(0, 361):
            a = math.radians(i)
            x = math.cos(a) * R
            z = math.sin(a) * R
            glVertex3f(x, 0.0, z)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
        glPopMatrix()

        # ---------- مدارها، سیاره‌ها، حلقه‌ی زحل، ماه زمین، لیبل‌ها ----------
        for i, (name, dist, rad, speed, color) in enumerate(planets):
            inc = inclinations[i]

            # مدار با شیب
            glPushMatrix()
            glRotatef(inc, 1, 0, 0)
            draw_orbit(dist)
            glPopMatrix()

            # موقعیت سیاره روی مدار
            ang = math.radians(angles[i])
            x_orbit = math.cos(ang) * dist
            z_orbit = math.sin(ang) * dist
            y_orbit = 0.0

            inc_rad = math.radians(inc)
            x_world = x_orbit
            y_world = y_orbit * math.cos(inc_rad) - z_orbit * math.sin(inc_rad)
            z_world = y_orbit * math.sin(inc_rad) + z_orbit * math.cos(inc_rad)

            planet_positions[i] = (x_world, y_world, z_world)

            is_focus = focus_mode and (i == focus_target)

            glPushMatrix()
            glTranslatef(x_world, y_world, z_world)
            glRotatef(angles[i] * 3.0, 0, 1, 0)

            # رنگ سیاره با intro_factor
            base_color = color
            planet_color = tuple(c * intro_factor for c in base_color)

            if is_focus and planet_textures[i] is not None:
                draw_textured_sphere(planet_textures[i], radius=rad * 1.2,
                                     slices=80, stacks=80)
            else:
                draw_colored_sphere(planet_color, radius=rad, slices=80, stacks=80)

            # حلقه‌ی زحل
            if name == "Saturn":
                inner = rad * 1.6
                outer = rad * 2.4
                draw_saturn_ring(inner, outer)

            # سیستم Earth–Moon
            if name == "Earth":
                glPushMatrix()
                moon_angle = angles[i] * 5.0
                a_m = math.radians(moon_angle)
                moon_dist = rad * 3.0
                mx = math.cos(a_m) * moon_dist
                mz = math.sin(a_m) * moon_dist
                glTranslatef(mx, 0.0, mz)
                moon_color = (0.8 * intro_factor, 0.8 * intro_factor, 0.85 * intro_factor)
                draw_colored_sphere(moon_color, radius=0.6, slices=40, stacks=40)
                glPopMatrix()

            glPopMatrix()

            # لیبل اسم سیاره بالای خودش
            label_y = y_world + rad + 1.5
            draw_3d_label(name, x_world, label_y, z_world, brightness=intro_factor)

            if not paused:
                angles[i] = (angles[i] + speed) % 360.0

        # آپدیت حرکات
        if not paused:
            sun_rotation = (sun_rotation + 0.3) % 360.0
            if focus_mode:
                camera_focus_angle = (camera_focus_angle + camera_speed_focus) % 360.0
            else:
                camera_angle_global = (camera_angle_global + camera_speed_global) % 360.0

        # ---------- پنل اطلاعات علمی در حالت فوکوس ----------
        if focus_mode:
            surface = pygame.display.get_surface()

            panel_width = 360
            panel_height = 200
            panel_rect = pygame.Rect(WIDTH - panel_width - 20, 40, panel_width, panel_height)

            # پس‌زمینه نیمه‌شفاف پنل
            panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            surface.blit(panel, panel_rect.topleft)

            # اسم سیاره و خطوط توضیح
            name = planets[focus_target][0]
            lines = planet_info.get(name, [])

            # عنوان
            title_surf = title_font.render(name, True, (255, 255, 255))
            surface.blit(title_surf, (panel_rect.x + 15, panel_rect.y + 10))

            # خطوط
            y_text = panel_rect.y + 45
            for line in lines:
                text_surf = info_font.render("• " + line, True, (220, 220, 220))
                surface.blit(text_surf, (panel_rect.x + 15, y_text))
                y_text += 24

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
