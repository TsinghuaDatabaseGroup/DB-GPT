# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import io
import base64
import datetime
import random

# matplotlib.pyplot 文档说明
# https://matplotlib.org/stable/api/pyplot_summary.html

def generate_prometheus_chart_content(title, values, x_label_format="'%Y-%m-%d %H:%M:%S'", size=(400, 225)):

    x_values = []
    y_values = []
    for item in values:
        date = datetime.datetime.fromtimestamp(item[0])
        formatted_date = date.strftime(x_label_format)
        x_values.append(formatted_date)
        y_values.append("{:.4f}".format(float(item[1])))
    return generate_chart_content(title, x_values, y_values, size)


def generate_chart_content(title, x_values, y_values, size=(400, 225)):
    image_base64 = plot(title, x_values, y_values, size)
    div_str = f'<img alt="" src="{image_base64}">'
    return div_str


def plot(title, x_values, y_values, size=(400, 225)):
    colors = ['#87CEEB', '#FF66CC', '#00C957', '#FFA500', '#9400D3', '#98FB98', '#007BA7', '#D2691E']
    random_color = random.choice(colors)

    plt.figure(figsize=(size[0]/60, size[1]/60), dpi=60)
    plt.plot(x_values, y_values, color=random_color, linewidth=1.0, alpha=1)
    plt.fill_between(x_values, y_values, color=random_color, alpha=0.2)
    plt.title(title, fontdict={'fontsize': 18})
    plt.xticks(rotation=45)
    ax = plt.gca()
    ax.spines['top'].set_color('#999999')
    ax.spines['right'].set_color('#999999')
    ax.spines['bottom'].set_color('#999999')
    ax.spines['left'].set_color('#999999')
    plt.grid(True)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)
    image_base64 = "data:image/jpg;base64," + \
        base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return image_base64


if __name__ == '__main__':

    # 测试数据，可使用浏览器打开test.html
    values = [
        [
            1695721125,
            "0.00033333332976326346"
        ],
        [
            1695721140,
            "0.0009999999989910673"
        ],
        [
            1695721155,
            "0.00033333333461390186"
        ],
        [
            1695721170,
            "0.0010000000038417056"
        ],
        [
            1695721185,
            "0.00033333333461390186"
        ],
        [
            1695721200,
            "0.0006666666643771654"
        ],
        [
            1695721215,
            "0.00033333333461390186"
        ],
        [
            1695721230,
            "0.0009999999989910673"
        ],
        [
            1695721245,
            "0.00033333333461390186"
        ],
        [
            1695721260,
            "0.0006666666692278037"
        ],
        [
            1695721275,
            "0.0009999999989910673"
        ],
        [
            1695721290,
            "0.0009999999989910673"
        ],
        [
            1695721305,
            "0.0006666666643771654"
        ],
        [
            1695721320,
            "0.0009999999989910673"
        ],
        [
            1695721335,
            "0.0009999999989910673"
        ],
        [
            1695721350,
            "0.0010000000038417056"
        ],
        [
            1695721365,
            "0.00033333333461390186"
        ]
    ]
    chart_content = generate_prometheus_chart_content('IO', values, x_label_format="%H:%M", size=(400, 225))
    # chart_content = generate_chart_content("CPU iRate", [1, 2, 3, 4, 5, 6], [1, 5, 3, 1, 9, 6])
    print(len(chart_content))
    with open("test.html", "w") as f:
        f.write(chart_content)
