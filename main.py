# -*- coding: utf-8 -*-
"""
自动轨迹绘制（教材：Python 基础教程 经典案例）

数据文件 trace_data.txt 每行格式：
    距离, 转向标志, 角度, R, G, B
  - 距离：海龟前进的像素数
  - 转向标志：0 表示左转，1 表示右转
  - 角度：转向的角度数
  - R,G,B：画笔颜色（0~1 浮点数）

思路：
1. 读取数据文件，把每行解析成 [距离, 转向, 角度, R, G, B] 列表；
2. 遍历数据，按每条指令设置颜色 → 前进 → 转向；
3. 绘制完成后把画布内容保存为结果截图。
"""
import turtle


def read_trace_data(path):
    """读取轨迹数据文件，返回 [[距离,转向,角度,R,G,B], ...]"""
    datalist = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.replace("\n", "").strip()
            if not line:
                continue
            datalist.append(list(map(eval, line.split(","))))
    return datalist


def draw_trace(datalist):
    """按数据指令自动绘制轨迹"""
    screen = turtle.Screen()
    screen.title("自动轨迹绘制")
    screen.setup(width=900, height=700)
    screen.tracer(False)  # 关闭动画，直接出最终图形
    t = turtle.Pen()
    t.pensize(3)
    t.speed(0)

    for cmd in datalist:
        dist, turn, angle, r, g, b = cmd
        t.pencolor(r, g, b)
        t.fd(dist)
        if turn == 0:
            t.left(angle)
        else:
            t.right(angle)

    screen.update()
    return t, screen


def save_canvas(screen, t, out_path):
    """把 turtle 画布窗口截取保存为 PNG（窗口置顶 + 等待渲染 + 重试校验）"""
    import time
    from PIL import ImageGrab, ImageStat

    canvas = t.getscreen().getcanvas()
    root = canvas.winfo_toplevel()
    root.attributes("-topmost", True)  # 强制窗口在最前
    root.lift()
    root.update()

    best = None
    for attempt in range(6):
        root.update_idletasks()
        root.update()
        screen.update()  # 重绘 turtle 画布内容
        time.sleep(1.0)  # 等窗口真正渲染出来
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        stat = ImageStat.Stat(img.convert("L"))
        stddev = stat.stddev[0]
        print(f"attempt {attempt}: pos=({x},{y}) size=({w}x{h}) stddev={stddev:.1f}")
        if stddev > 10:  # 画面有内容（不是纯色背景）
            img.save(out_path)
            print("已保存截图:", out_path)
            return
        if best is None or stddev > 5:
            best = img
    if best:
        best.save(out_path)
        print("已保存截图(低置信):", out_path)


def main():
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 解决 DPI 缩放坐标错位
    except Exception:
        pass
    datalist = read_trace_data("trace_data.txt")
    print("读取到", len(datalist), "条轨迹指令")
    t, screen = draw_trace(datalist)
    save_canvas(screen, t, "screenshots/trace_result.png")
    turtle.bye()  # 不进入 mainloop，截完图直接退出


if __name__ == "__main__":
    main()
