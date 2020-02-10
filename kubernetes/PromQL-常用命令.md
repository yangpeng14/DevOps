## PromQL 用途

> PromQL 可以非常方便的对监控样本数据进行统计分析，PromQL 支持常见运算符和一些内置的函数，监控告警也是依赖PromQL实现的。

## 时间序列
在时间序列中，每一个点称之为样本，每个样本由三部分组成：

- 指标：由指标名称和描述指标的级别组成的。
- 时间戳：一个精确到毫秒级别的时间戳
- 值：一个`float64`位的值

```
<--------------- metric="" ---------------------=""><-timestamp -=""><-value->

http_request_total{status=”200”, method=”GET”}@1434417560938 => 94355
```

### 指标

形式上所有的指标都是由如下的格式标示：

> {=, …}

在`Prometheus`的底层实现中指标名称实际上是以`__name__=<metric name>`的形式保存在数据库中的。

> api_http_requests_total{method=”POST”, handler=”/messages”}

等价于

> {name=”api_http_requests_total”，method=”POST”, handler=”/messages”}

所以底层存储的是`map[string]string`.如下是`Promtheus`中的`Metric`的源码。

```go
type Metric LabelSet

type LabelSet map[LabelName]LabelValue

type LabelName string

type LabelValue string
```

### Metric 类型

> 每一种指标标示的意义都不一样，因此对应的类型不一样，比如系统负载是随着时间变化而变化的值，cpu使用时间是一个一直递增的值，只要系统不重启。

- Counter：只增不减的计数器
- Gauge：可增可减的仪表盘
- Histogram和Summary分析数据分布情况

## 初识 PromQL

### 运算符

- 等于：`http_requests_total{instance="localhost:9090"}`

- 不等于：`http_requests_total{instance!="localhost:9090"}`

- 匹配：`http_requests_total{environment=~"staging|testing|development",method!="GET"}` 多个值用`|`连接。

- 排除：`http_requests_total{environment!~"staging|testing|development",method!="GET"}`不存在这几个值之间。

- 范围查询：`http_request_total{}[5m] 5m`以内的数据，这叫区间数据，还有瞬时数据，只返回最近的一条`http_request_total{}`。还支持如下的时间范围查询。
    - s - 秒
    - m - 分钟
    - h - 小时
    - d - 天
    - w - 周
    - y - 年

- 时间位移：选择一个参考点，上面的范围查询都是使用的是当前的时间值，位移操作的关键字为`offset`

```
http_request_total{} offset 5m
http_request_total{}[1d] offset 1d
```

- 聚合操作：
    - `sum`函数：对指标进行求和，如：`sum(http_request_total)`
    - `avg`函数：对指标进行求平均值。

## 操作符

### 运算符

- `+` (加法)
- `-` (减法)
- `*` (乘法)
- `/` (除法)
- `%` (求余)
- `^` (幂运算)

当瞬时向量与标量之间进行数学运算时，数学运算符会依次作用域瞬时向量中的每一个样本值，从而得到一组新的时间序列。如

`node_memory_free_bytes_total / (1024 * 1024)`

如果是瞬时向量与瞬时向量之间进行数学运算时，左边向量元素匹配（标签完全一致）右边向量元素，如果没找到匹配元素，则直接抛弃。如下两个指标进行相加操作，唯一不同的就是值，连时间戳都是一样的。

```
{device="sda",instance="localhost:9100",job="node_exporter"}=>1634967552@1518146427.807 + 864551424@1518146427.807

{device="sdb",instance="localhost:9100",job="node_exporter"}=>0@1518146427.807 + 1744384@1518146427.807
```

### 布尔运算

瞬时向量与标量进行布尔运算时，`PromQL`依次比较向量中的所有时间序列样本的值，如果比较结果为`true`则保留，反之丢弃。

- `==` (相等)
- `!=` (不相等)
- `>` (大于)
- `<` (小于)
- `>=` (大于等于)
- `<=` (小于等于)

### bool 修饰符

`bool`修饰符，使用`bool`修改符后，布尔运算不会对时间序列进行过滤，而是直接依次瞬时向量中的各个样本数据与标量的比较结果`0`或者`1`。从而形成一条新的时间序列.和上面的图进行对比。

### 集合运行

- `and` (并且)
- `or` (或者)
- `unless` (排除)

`vector1 and vector2` 会产生一个由vector1的元素组成的新的向量。该向量包含vector1中完全匹配vector2中的元素组成。

`vector1 or vector2` 会产生一个新的向量，该向量包含vector1中所有的样本数据，以及vector2中没有与vector1匹配到的样本数据。

`vector1 unless vector2` 会产生一个新的向量，新向量中的元素由vector1中没有与vector2匹配的元素组成。

### 操作符优先级

如下计算每个实例上每个核心cpu的使用率:

```
100 * (1-avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance,cpu))
```
在PromQL操作符中优先级由高到低依次为：

- `^`
- `*, /, %`
- `+, -`
- `==, !=, <=, <, >=, >`
- `and, unless`
- `or`

### 向量匹配模式详解

向量与向量之间运算时会基于默认的匹配规则，依次找到右边边向量元素和左边向量元素匹配(标签完全一致)的进行运算，不匹配则丢弃。在`PromQL`中有两种典型的匹配模式。

#### 一对一（one to one）
一对一匹配模式会从操作符两边获取瞬时向量依次比较并找到唯一匹配的样本值，使用的表达式如下：
```
vector1 <operator> vector2
```

在操作符两边表达式标签不一致的情况下，可以使用`on(label list)`或者`ignoring(label list）`来修改便签的匹配行为。使用`ignoreing`可以在匹配时忽略某些便签。而`on`则用于将匹配行为限定在某些便签之内。

```
<vector expr> <bin-op> ignoring(<label list>) <vector expr>
<vector expr> <bin-op> on(<label list>) <vector expr>
```

例如当存在样本：

```
method_code:http_errors:rate5m{method="get", code="500"}  24
method_code:http_errors:rate5m{method="get", code="404"}  30
method_code:http_errors:rate5m{method="put", code="501"}  3
method_code:http_errors:rate5m{method="post", code="500"} 6
method_code:http_errors:rate5m{method="post", code="404"} 21


method:http_requests:rate5m{method="get"}  600
method:http_requests:rate5m{method="del"}  34
method:http_requests:rate5m{method="post"} 120
```

使用PromQL表达式：使用了`ignoring`之后忽略了第一组向量的`code`标签，这样就和第二组向量拥有一样的标签了。

```
method_code:http_errors:rate5m{code="500"} / ignoring(code) method:http_requests:rate5m
```

该表达式会返回在过去5分钟内，HTTP请求状态码为500的在所有请求中的比例。如果没有使用`ignoring(code)`，操作符两边表达式返回的瞬时向量中将找不到任何一个标签完全相同的匹配项。

因此结果如下：

```
{method="get"}  0.04            //  24 / 600
{method="post"} 0.05            //   6 / 120
```

同时由于`method`为`put`和`del`的样本找不到匹配项，因此不会出现在结果当中。

#### 多对一和一对多

多对一和一对多两种匹配模式指的是“一”侧的每一个向量元素可以与”多”侧的多个元素匹配的情况。在这种情况下，必须使用`group`修饰符：`group_left`或者`group_right`来确定哪一个向量具有更高的基数（充当“多”的角色）。

```
<vector expr> <bin-op> ignoring(<label list>) group_left(<label list>) <vector expr>
<vector expr> <bin-op> ignoring(<label list>) group_right(<label list>) <vector expr>
<vector expr> <bin-op> on(<label list>) group_left(<label list>) <vector expr>
<vector expr> <bin-op> on(<label list>) group_right(<label list>) <vector expr>
```

多对一和一对多两种模式一定是出现在操作符两侧表达式返回的向量标签不一致的情况。因此需要使用`ignoring`和`on`修饰符来排除或者限定匹配的标签列表。

例如,使用表达式：
```
method_code:http_errors:rate5m / ignoring(code) group_left method:http_requests:rate5m
```

该表达式中，左向量`method_code:http_errors:rate5m`包含两个标签`method`和`code`。而右向量`method:http_requests:rate5m`中只包含一个标签`method`，因此匹配时需要使用`ignoring`限定匹配的标签为`code`。 在限定匹配标签后，右向量中的元素可能匹配到多个左向量中的元素 因此该表达式的匹配模式为多对一，需要使用`group`修饰符`group_left`指定左向量具有更好的基数。

最终的运算结果如下：

```
{method="get", code="500"}  0.04            //  24 / 600
{method="get", code="404"}  0.05            //  30 / 600
{method="post", code="500"} 0.05            //   6 / 120
{method="post", code="404"} 0.175           //  21 / 120
```

> 提醒：`group`修饰符只能在比较和数学运算符中使用。在逻辑运算`and`,`unless`和`or`中默认与右向量中的所有元素进行匹配。

## 聚合操作

`Prometheus`提供了一些内置的聚合操作符，这些操作符只能作用于瞬时向量，可以将瞬时表达式返回的样本数据进行聚合，形成一个新的时间序列。内置的聚合函数如下：

- `sum` (求和)
- `min` (最小值)
- `max` (最大值)
- `avg` (平均值)
- `stddev` (标准差)
- `stdvar` (标准差异)
- `count` (计数)
- `count_values` (对value进行计数)
- `bottomk` (后n条时序)
- `topk` (前n条时序)
- `quantile` (分布统计)

使用聚合操作的语法如下：

```
<aggr-op>([parameter,] <vector expression>) [without|by (<label list>)]
```

其中只有`count_values`, `quantile`, `topk`, `bottomk`支持参数(parameter)。`aggr-op`就是上面的聚合函数。

`without`用于移除计算结果中的标签,`by`则相反，只保留此标签。通过`without`和`by`可以按照样本的问题对数据进行聚合。

## PromQL 内置函数

### 计算`Counter`类型的指标增长率

- `increase(v range-vector)`函数：获取区间向量的增长量

- `rate(v range-vector)`函数：rate函数可以直接计算区间向量v在时间窗口内平均增长速率

    ```
    rate(node_cpu[2m])
    increase(node_cpu[2m]) / 120 
    上面的两个计算结果是一致的，increase(node_cpu[2m])获取的是两分钟之内的增长量，除以120s之后得到的就是两分钟之间的平均增长率。
    ```

- `irate(v range-vector)`函数：`irate`函数是通过区间向量中最后两个两本数据来计算区间向量的增长速率,计算的是一个瞬时增长速率。

### 预测Gauge指标变化趋势

- `predict_linear(v range-vector, t scalar)`函数：基于简单的线性回归的方式进行`t`秒后的`v`值的预测。

## 原谅出处

> 作者：菜鸟随笔

> 原文链接：https://lengrongfu.github.io/2019/03/17/PromQL-%E5%B8%B8%E7%94%A8%E5%91%BD%E4%BB%A4