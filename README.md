# StarRailAutoPilot
基于小地图寻路的锄大地脚本

由于是非常早期的开发版本，目前需要先移动到对应的地图，StarRailAutoPilot.py中设置好路线编号，并在起始点开启脚本。

## 功能列表
- 定位坐标 已经完成
- 开拓模式（根据路线图寻路）：基本完成
- 巡猎模式（小地图遇敌时，根据敌人位置进行攻击）：目前还没加战斗判定
- 主角模式（将可破坏物也一并收集）：暂时没实现，应该添加一种新的标点就可以了
- 可视化路线：根据导航点可视化路线
- 自动寻路：基于jps以及Astar算法自动寻找点位，目前效果不如绘制的路线

## 如何绘制路线图

maps文件夹中存储了地图的原图以及路线图(xx-x.png)。复制一份原图，在图上直接画点，不同RGB颜色代表不同的点：
1. 出发点：H==180 青色 仅有一个
2. 开拓导航点：（H==60 黄色）到达后不会进行任何动作，最常用的导航点
3. 巡猎导航点：（H==10 红色）到达后会主动开启巡猎模式，孽物速速受死！
4. 可破坏物导航点：（H==40 橙色）到达后会尝试进行一次攻击，一般用来收集垃圾桶，爷（「星」/「穹」）的最爱。没必要标在可破坏物的实际位置上，能攻击到就行。是否要区分开所有的可破坏物（血瓶、秘技瓶、垃圾桶等）有待考虑

导航点排序依据：
先根据 S 值降序排序
S值相同时，选择离当前点最近的点作为下一个点。

运行visualize_route.py可以在debug文件夹中批量生成可视化的路线。

目前暂时是根据离当前点最近的点作为下一个点，所以标点的时候要注意尽量不要出现锐角。后续可能会使用颜色的饱和度或者亮度作为先后排序依据。
后续可能会加入：入画点、电梯操作点等特殊操作点位


## 相关项目

- JPS寻路 https://github.com/ViktorRubenko/Jump-Point-Search
- 自动锄大地 https://github.com/Starry-Wind/StarRailAssistant
- 自动模拟宇宙 https://github.com/CHNZYX/Auto_Simulated_Universe
