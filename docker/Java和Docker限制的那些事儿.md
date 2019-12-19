## 揭秘

Java和Docker不是天然的朋友。 Docker可以设置内存和CPU限制，而Java不能自动检测到。使用Java的Xmx标识（繁琐/重复）或新的实验性JVM标识，我们可以解决这个问题。

## 虚拟化中的不匹配

Java和Docker的结合并不是完美匹配的，最初的时候离完美匹配有相当大的距离。对于初学者来说，JVM的全部设想就是，虚拟机可以让程序与底层硬件无关。

那么，把我们的Java应用打包到JVM中，然后整个再塞进Docker容器中，能给我们带来什么好处呢？大多数情况下，你只是在复制JVMs和Linux容器，除了浪费更多的内存，没任何好处。感觉这样子挺傻的。

不过，Docker可以把你的程序，设置，特定的JDK，Linux设置和应用服务器，还有其他工具打包在一起，当做一个东西。站在DevOps/Cloud的角度来看，这样一个完整的容器有着更高层次的封装。

### 问题一：内存

时至今日，绝大多数产品级应用仍然在使用Java 8（或者更旧的版本），而这可能会带来问题。Java 8（update 131之前的版本）跟Docker无法很好地一起工作。问题是在你的机器上，JVM的可用内存和CPU数量并不是Docker允许你使用的可用内存和CPU数量。

比如，如果你限制了你的Docker容器只能使用100MB内存，但是呢，旧版本的Java并不能识别这个限制。Java看不到这个限制。JVM会要求更多内存，而且远超这个限制。如果使用太多内存，Docker将采取行动并杀死容器内的进程！JAVA进程被干掉了，很明显，这并不是我们想要的。

为了解决这个问题，你需要给Java指定一个最大内存限制。在旧版本的Java（8u131之前），你需要在容器中通过设置-Xmx来限制堆大小。这感觉不太对，你可不想定义这些限制两次，也不太想在你的容器中来定义。

幸运的是我们现在有了更好的方式来解决这个问题。从Java 9之后（8u131+），JVM增加了如下标志：

```
-XX:+UnlockExperimentalVMOptions -XX:+UseCGroupMemoryLimitForHeap
```

这些标志强制JVM检查Linux的cgroup配置，Docker是通过cgroup来实现最大内存设置的。现在，如果你的应用到达了Docker设置的限制（比如500MB），JVM是可以看到这个限制的。JVM将会尝试GC操作。如果仍然超过内存限制，JVM就会做它该做的事情，抛出OutOfMemoryException。也就是说，JVM能够看到Docker的这些设置。

从Java 10之后（参考下面的测试），这些体验标志位是默认开启的，也可以使用-XX:+UseContainerSupport来使能（你可以通过设置-XX:-UseContainerSupport来禁止这些行为）。

### 问题二：CPU

第二个问题是类似的，但它与CPU有关。简而言之，JVM将查看硬件并检测CPU的数量。它会优化你的runtime以使用这些CPUs。但是同样的情况，这里还有另一个不匹配，Docker可能不允许你使用所有这些CPUs。可惜的是，这在Java 8或Java 9中并没有修复，但是在Java 10中得到了解决。

从Java 10开始，可用的CPUs的计算将采用以不同的方式（默认情况下）解决此问题（同样是通过UseContainerSupport）。

## Java和Docker的内存处理测试

作为一个有趣的练习，让我们验证并测试Docker如何使用几个不同的JVM版本/标志甚至不同的JVM来处理内存不足。

首先，我们创建一个测试应用程序，它只是简单地“吃”内存并且不释放它。

```java
import java.util.ArrayList;
import java.util.List;
public class MemEat {
    public static void main(String[] args) {
        List l = new ArrayList<>();
        while (true) {
            byte b[] = new byte[1048576];
            l.add(b);
            Runtime rt = Runtime.getRuntime();
            System.out.println( "free memory: " + rt.freeMemory() );
        }
    }
}
```

我们可以启动Docker容器并运行这个应用程序来查看会发生什么。

### 测试一：Java 8u111

首先，我们将从具有旧版本Java 8的容器开始（update 111）。

```bash
docker run -m 100m -it java:openjdk-8u111 /bin/bash
```

我们编译并运行MemEat.java文件：

```bash
javac MemEat.java
java MemEat
...
free memory: 67194416
free memory: 66145824
free memory: 65097232
Killed
```

正如所料，Docker已经杀死了我们的Java进程。不是我们想要的（！）。你也可以看到输出，Java认为它仍然有大量的内存需要分配。

我们可以通过使用-Xmx标志为Java提供最大内存来解决此问题：

```
javac MemEat.java
java -Xmx100m MemEat
...
free memory: 1155664
free memory: 1679936
free memory: 2204208
free memory: 1315752
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
    at MemEat.main(MemEat.java:8)
```

在提供了我们自己的内存限制之后，进程正常停止，JVM理解它正在运行的限制。然而，问题在于你现在将这些内存限制设置了两次，Docker一次，JVM一次。

### 测试二：Java 8u144

如前所述，随着增加新标志来修复问题，JVM现在可以遵循Docker所提供的设置。我们可以使用版本新一点的JVM来测试它。

```bash
docker run -m 100m -it adoptopenjdk/openjdk8 /bin/bash
```

（在撰写本文时，此OpenJDK Java镜像的版本是Java 8u144）

接下来，我们再次编译并运行MemEat.java文件，不带任何标志：

```
javac MemEat.java
java MemEat
...
free memory: 67194416
free memory: 66145824
free memory: 65097232
Killed
```

依然存在同样的问题。但是我们现在可以提供上面提到的实验性标志来试试看：

```
javac MemEat.java
java -XX:+UnlockExperimentalVMOptions -XX:+UseCGroupMemoryLimitForHeap MemEat
...
free memory: 1679936
free memory: 2204208
free memory: 1155616
free memory: 1155600
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
   at MemEat.main(MemEat.java:8)
```

这一次我们没有告诉JVM限制的是什么，我们只是告诉JVM去检查正确的限制设置！现在感觉好多了。

### 测试三：Java 10u23

有些人在评论和Reddit上提到Java 10通过使实验标志成为新的默认值来解决所有问题。这种行为可以通过禁用此标志来关闭：-XX：-UseContainerSupport。

当我测试它时，它最初不起作用。在撰写本文时，AdoptAJDK OpenJDK10镜像与jdk-10+23一起打包。这个JVM显然还是不理解UseContainerSupport标志，该进程仍然被Docker杀死。

```bash
docker run -m 100m -it adoptopenjdk/openjdk10 /bin/bash
```

测试了代码（甚至手动提供需要的标志）：

```
javac MemEat.java
java MemEat
...
free memory: 96262112
free memory: 94164960
free memory: 92067808
free memory: 89970656
Killed
java -XX:+UseContainerSupport MemEat
Unrecognized VM option 'UseContainerSupport'
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.
```

### 测试四：Java 10u46（Nightly）

我决定尝试AdoptAJDK OpenJDK 10的最新nightly构建。它包含的版本是Java 10+46，而不是Java 10+23。

```bash
docker run -m 100m -it adoptopenjdk/openjdk10:nightly /bin/bash
```

然而，在这个ngithly构建中有一个问题，导出的PATH指向旧的Java 10+23目录，而不是10+46，我们需要修复这个问题。

```
export PATH=$PATH:/opt/java/openjdk/jdk-10+46/bin/
javac MemEat.java
java MemEat
...
free memory: 3566824
free memory: 2796008
free memory: 1480320
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
  at MemEat.main(MemEat.java:8)
```

成功！不提供任何标志，Java 10依然可以正确检测到Dockers内存限制。

### 测试五：OpenJ9

我最近也在试用OpenJ9，这个免费的替代JVM已经从IBM J9开源，现在由Eclipse维护。

请在我的下一篇博文 http://royvanrijn.com/blog/2018/05/openj9-jvm-shootout/ 阅读关于OpenJ9的更多信息。

它运行速度快，内存管理非常好，性能卓越，经常可以为我们的微服务节省多达30-50％的内存。这几乎可以将Spring Boot应用程序定义为’micro’了，其运行时间只有100-200mb，而不是300mb+。我打算尽快就此写一篇关于这方面的文章。

但令我惊讶的是，OpenJ9还没有类似于Java 8/9/10+中针对cgroup内存限制的标志（backported）的选项。如果我们将以前的测试用例应用到最新的AdoptAJDK OpenJDK 9 + OpenJ9 build：

```bash
docker run -m 100m -it adoptopenjdk/openjdk9-openj9 /bin/bash
```

我们添加OpenJDK标志（OpenJ9会忽略的标志）：

```
java -XX:+UnlockExperimentalVMOptions -XX:+UseCGroupMemoryLimitForHeap MemEat
...
free memory: 83988984
free memory: 82940400
free memory: 81891816
Killed
```

Oops，JVM再次被Docker杀死。

我真的希望类似的选项将很快添加到OpenJ9中，因为我希望在生产环境中运行这个选项，而不必指定最大内存两次。 Eclipse/IBM正在努力修复这个问题，已经提了issues，甚至已经针对issues提交了PR。

### 更新：（不推荐Hack）

一个稍微丑陋/hacky的方式来解决这个问题是使用下面的组合标志：

```
java -Xmx`cat /sys/fs/cgroup/memory/memory.limit_in_bytes` MemEat
...
free memory: 3171536
free memory: 2127048
free memory: 2397632
free memory: 1344952
JVMDUMP039I Processing dump event "systhrow", detail "java/lang/OutOfMemoryError" at 2018/05/15 14:04:26 - please wait.
JVMDUMP032I JVM requested System dump using '//core.20180515.140426.125.0001.dmp' in response to an event
JVMDUMP010I System dump written to //core.20180515.140426.125.0001.dmp
JVMDUMP032I JVM requested Heap dump using '//heapdump.20180515.140426.125.0002.phd' in response to an event
JVMDUMP010I Heap dump written to //heapdump.20180515.140426.125.0002.phd
JVMDUMP032I JVM requested Java dump using '//javacore.20180515.140426.125.0003.txt' in response to an event
JVMDUMP010I Java dump written to //javacore.20180515.140426.125.0003.txt
JVMDUMP032I JVM requested Snap dump using '//Snap.20180515.140426.125.0004.trc' in response to an event
JVMDUMP010I Snap dump written to //Snap.20180515.140426.125.0004.trc
JVMDUMP013I Processed dump event "systhrow", detail "java/lang/OutOfMemoryError".
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
  at MemEat.main(MemEat.java:8)
```

在这种情况下，堆大小受限于分配给Docker实例的内存，这适用于较旧的JVM和OpenJ9。这当然是错误的，因为容器本身和堆外的JVM的其他部分也使用内存。但它似乎工作，显然Docker在这种情况下是宽松的。也许某些bash大神会做出更好的版本，从其他进程的字节中减去一部分。

无论如何，不要这样做，它可能无法正常工作。

### 测试六：OpenJ9（Nightly）

有人建议使用OpenJ9的最新nightly版本。

```bash
docker run -m 100m -it adoptopenjdk/openjdk9-openj9:nightly /bin/bash
```

最新的OpenJ9夜间版本，它有两个东西：

1. 另一个有问题的PATH参数，需要先解决这个问题
2. JVM支持新标志UseContainerSupport（就像Java 10一样）

```
export PATH=$PATH:/opt/java/openjdk/jdk-9.0.4+12/bin/
javac MemEat.java
java -XX:+UseContainerSupport MemEat
...
free memory: 5864464
free memory: 4815880
free memory: 3443712
free memory: 2391032
JVMDUMP039I Processing dump event "systhrow", detail "java/lang/OutOfMemoryError" at 2018/05/15 21:32:07 - please wait.
JVMDUMP032I JVM requested System dump using '//core.20180515.213207.62.0001.dmp' in response to an event
JVMDUMP010I System dump written to //core.20180515.213207.62.0001.dmp
JVMDUMP032I JVM requested Heap dump using '//heapdump.20180515.213207.62.0002.phd' in response to an event
JVMDUMP010I Heap dump written to //heapdump.20180515.213207.62.0002.phd
JVMDUMP032I JVM requested Java dump using '//javacore.20180515.213207.62.0003.txt' in response to an event
JVMDUMP010I Java dump written to //javacore.20180515.213207.62.0003.txt
JVMDUMP032I JVM requested Snap dump using '//Snap.20180515.213207.62.0004.trc' in response to an event
JVMDUMP010I Snap dump written to //Snap.20180515.213207.62.0004.trc
JVMDUMP013I Processed dump event "systhrow", detail "java/lang/OutOfMemoryError".
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
```

TADAAA，正在修复中！

奇怪的是，这个标志在OpenJ9中默认没有启用，就像它在Java 10中一样。再说一次：确保你测试了这是你想在一个Docker容器中运行Java。

## 结论

简言之：注意资源限制的不匹配。测试你的内存设置和JVM标志，不要假设任何东西。

如果您在Docker容器中运行Java，请确保你设置了Docker内存限制和在JVM中也做了限制，或者你的JVM能够理解这些限制。

如果您无法升级您的Java版本，请使用-Xmx设置您自己的限制。

对于Java 8和Java 9，请更新到最新版本并使用：

```
-XX：+UnlockExperimentalVMOptions -XX：+UseCGroupMemoryLimitForHeap
```

对于Java 10，确保它支持’UseContainerSupport’（更新到最新版本）。

对于OpenJ9（我强烈建议使用，可以在生产环境中有效减少内存占用量），现在使用-Xmx设置限制，但很快会出现一个支持UseContainerSupport标志的版本。

## 原文出处
> http://royvanrijn.com/blog/2018/05/java-and-docker-memory-limits/

## 译文出处
> http://team.jiunile.com/blog/2018/07/docker-java%E4%B8%8Edocker%E7%9A%84%E9%82%A3%E7%82%B9%E4%BA%8B.html