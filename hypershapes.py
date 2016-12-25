# Only works with Python 2
# You must have tkinter and numpy installed.

import numpy as np
import math
import Tkinter as tk
import tkFileDialog as filedialog
from ScrolledText import ScrolledText
import gtk
import itertools
import random
import sys
import os
import ast


def open_in_text_editor(f):
    os.system(("notepad {}" if "win" in sys.platform else "xdg-open {} &").format(f))


def point_on_sphere(radius, angles):
    point = []
    dims = len(angles)+1
    for i in range(dims-1):
        coord = radius
        for j in range(i):
            coord *= math.sin(angles[j])
        coord *= math.cos(angles[i])
        point.append(coord)
    coord = radius
    for i in range(dims-1):
        coord *= math.sin(angles[i])
    point.append(coord)
    return np.array(point)


def transform(matrix, points):
    # matrix :: np matrix
    # quality :: Double
    # radius :: Double
    # location :: np vector

    ans = np.matmul(matrix, points.transpose()).transpose() + np.array([WIDTH/2, HEIGHT/2])
    return ans


def sphere_points(radius, dims, quality):
    return np.array([point_on_sphere(radius, angles) for angles in itertools.product(*[list(np.arange(0, 2 * math.pi, 1.0 / quality)) for _ in range(dims - 1)])])


def cube_points(radius, dims, quality):
    pointss = []
    for i in range(dims):
        for c_i in [-radius, radius]:
            points = list(itertools.product(*[list(np.arange(-radius, radius, 100.0/quality)) for _ in range(dims - 1)]))
            for i in range(len(points)):
                points[i] = list(points[i])
                points[i].insert(i, c_i)
        pointss += points
    return np.array(pointss)


def show_points(points, color="black", size=1):
    for point in points:
        x0 = point[0] - size
        y0 = point[1] - size
        x1 = point[0] + size
        y1 = point[1] + size

        canvas.create_oval(x0, y0, x1, y1, fill=color, width=0)


class Object:
    def __init__(self, t, properties):
        self.type = t
        self.properties = properties

    def show(self):
        if self.type == "sphere":
            dims = self.properties["matrix"].shape[1]
            show_points(transform(self.properties["matrix"], sphere_points(self.properties["radius"], dims, self.properties["quality"])), self.properties["color"], self.properties["size"])
        elif self.type == "cube":
            dims = self.properties["matrix"].shape[1]
            show_points(transform(self.properties["matrix"],
                                  cube_points(self.properties["radius"], dims, self.properties["quality"])),
                        self.properties["color"], self.properties["size"])

    def __str__(self):
        return str(dict(self.properties, type=self.type))


def read_object(string):
    d = ast.literal_eval(string)
    d["matrix"] = np.array(d["matrix"])
    t = d["type"]
    d.pop("type")
    return Object(t, d)


def render():
    try:
        canvas.create_rectangle(0, 0, WIDTH+1, HEIGHT+1, fill="white", width=0)
        float_props = [("quality", quality), ("radius", radius)]
        for p, q in float_props:
            obj.properties[p] = float(q.get())

        obj.properties["matrix"] = np.array([[float(n) for n in a.split(" ")] for a in filter(lambda x: x != "", matrix_entry.get("0.0", tk.END).split("\n"))])

        obj.show()
    except ValueError:
        print "Error - invalid property"


def save():
    name = filedialog.asksaveasfilename(defaultextension=".hyp", filetypes=[("Hypershape", "*.hyp"), ("Other", "*.*")])
    obj.properties["matrix"] = [list(a) for a in list(obj.properties["matrix"])]
    f = open(name, "w")
    f.write(str(obj))
    f.close()
    obj.properties["matrix"] = np.array(obj.properties["matrix"])
    print "Saved to {}".format(name)


def open_object():
    global obj
    name = filedialog.askopenfilename(defaultextension=".hyp", filetypes=[("Hypershape", "*.hyp"), ("Other", "*.*")])
    obj = read_object(open(name).read())
    show_properties()


def create_sphere():
    global obj
    buttons.destroy()
    angles = [random.random() * 2 * math.pi for i in range(4)]
    obj = Object("sphere", {"matrix": np.array([[math.cos(a), math.sin(a)] for a in angles]).transpose(), "quality": 5,
                            "radius": 3 * HEIGHT / 8, "size": 1, "color": "black"})
    obj.show()
    show_properties()


def create_cube():
    global obj
    buttons.destroy()
    angles = [random.random() * 2 * math.pi for i in range(4)]
    obj = Object("cube", {"matrix": np.array([[math.cos(a), math.sin(a)] for a in angles]).transpose(), "quality": 5,
                          "radius": 3 * HEIGHT / 8, "size": 1, "color": "black"})
    obj.show()
    show_properties()


def show_properties():
    global properties, quality, radius, matrix_entry
    properties = tk.Frame(root)
    properties.grid(row=0, column=1, sticky=tk.NW)

    quality = tk.StringVar(root, str(obj.properties["quality"]))
    quality_label = tk.Label(properties, text="Quality: ")
    quality_label.grid(row=0, column=0)
    quality_entry = tk.Spinbox(properties, from_=1, increment=0.1, to=100, textvariable=quality, bg="white")
    quality_entry.grid(row=0, column=1)

    radius = tk.StringVar(root, str(obj.properties["radius"]))
    radius_label = tk.Label(properties, text="Radius: ")
    radius_label.grid(row=1, column=0)
    radius_entry = tk.Spinbox(properties, from_=0, increment=10, to=1e100, textvariable=radius, bg="white")
    radius_entry.grid(row=1, column=1)

    matrix_entry = ScrolledText(properties, bg="white")
    matrix_entry.insert("0.0", "\n".join([" ".join([str(a) for a in row]) for row in obj.properties["matrix"]]))
    matrix_entry.grid(row=3, column=0, columnspan=2)

    render_button = tk.Button(properties, text="Render", command=render)
    render_button.grid(row=4, column=0)


def quit_():
    # TODO: Add are you sure?
    root.destroy()

# winfo_screenwidth gets the total width of all the monitors.
window = gtk.Window()
screen = window.get_screen()
monitors = []
num_mons = screen.get_n_monitors()
for m in range(num_mons):
    mg = screen.get_monitor_geometry(m)
    monitors.append(mg)
cur_mon = screen.get_monitor_at_window(screen.get_active_window())
_, _, WIDTH, HEIGHT = monitors[cur_mon]
print "Monitor resolution: {}x{}".format(WIDTH, HEIGHT)


root = tk.Tk()
root.title("Hypershapes")
root.attributes("-fullscreen", True)

menu = tk.Menu(root)

fileMenu = tk.Menu(menu, tearoff=0)
fileMenu.add_command(label="Open", command=open_object, accelerator="Ctrl+O")
fileMenu.add_command(label="Save", command=save, accelerator="Ctrl+S")
fileMenu.add_command(label="Quit", command=quit_, accelerator="Ctrl+Q")
menu.add_cascade(label="File", menu=fileMenu)

root.config(menu=menu)

canvas = tk.Canvas(root, width=3*WIDTH/4, height=HEIGHT, bg="white")
canvas.grid(row=0, column=0)

buttons = tk.Frame(root)
buttons.grid(row=0, column=1, sticky=tk.NW)

sphere = tk.Button(buttons, text="Sphere", command=create_sphere)
sphere.grid(row=0, column=0, sticky=tk.NW)

cube = tk.Button(buttons, text="Cube", command=create_cube)
cube.grid(row=1, column=0, sticky=tk.NW)

root.bind("<Control-q>", lambda x: quit_())
root.bind("<Control-s>", lambda x: save())
root.bind("<Control-o>", lambda x: open_object())
root.mainloop()
