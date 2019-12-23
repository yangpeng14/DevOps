## Cronjob 简介

`Cronjob` 是一个计划任务，与 Linux 系统 Crontab 一样，格式也是基本一样。

`格式如下`：

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * command to execute
```

具体见 https://en.wikipedia.org/wiki/Cron#Overview

## Cronjob 结构草图

![](/img/k8s-cron.png)

## Cronjob 运行
`CronJob` 使用 [Job](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/) 对象来完成任务。`CronJob` 每次运行时都会创建一个 `Job` 对象，`Job` 会创建一个 `Pods` 来执行任务，任务执行完成后停止容器。

## Cronjob 用途

`CronJob` 在特定时间 或 按特定间隔运行任务。`CronJob` 非常适合用于自动执行任务，例如备份、报告、发送电子邮件或清理任务。

## Cronjob 例子

```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: demo # Cronjob的名称
  labels:
    app: demo
    cron: hello
spec:
  concurrencyPolicy: Forbid
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: demo
            cron: hello
        spec:
          containers:
          - image: harbor.example.com/hello:v1
            imagePullPolicy: IfNotPresent
            name: hello
            command: [/bin/bash]
            args:
            - -c
            - echo "Hello World!!!" # job 具体执行的任务
            resources:
              limits:
                cpu: 300m
                memory: 300Mi
              requests:
                cpu: 100m
                memory: 100Mi
          nodeSelector:
            label: test
          imagePullSecrets:
            - name: harbor-certification
          restartPolicy: Never
  schedule: "15 * * * *"  # job执行的周期，cron格式的字符串
  successfulJobsHistoryLimit: 1
```

## Cronjob 重要参数解释

- 调度

    `.spec.schedule` 是 `.spec` 中必需的字段，它的值是 `Cron` 格式字的符串，例如：0 * * * *，或者 @hourly，根据指定的调度时间 `Job` 会被创建和执行。

- 启动 Job 的期限（秒级别）

    `.spec.startingDeadlineSeconds `字段是可选的。它表示启动 Job 的期限（秒级别），如果因为任何原因而错过了被调度的时间，那么错过执行时间的 Job 将被认为是失败的。如果没有指定，则没有期限。

- Job 历史版本限制

    - `.spec.successfulJobsHistoryLimit`：# 字段是可选的，成功完成的作业保存多少个
    - `.spec.failedJobsHistoryLimit`：    # 字段是可选的，失败的作业保存多少个

    默认没有限制，所有成功和失败的 Job 都会被保留。然而，当运行一个 Cron Job 时，很快就会堆积很多 Job，推荐设置这两个字段的值。设置为0则不会保存，这两个字段与jobTemplate同级。

- 并发策略

    `.spec.concurrencyPolicy` 字段也是可选的。它指定了如何处理被 Cron Job 创建的 Job 的并发执行。只允许指定下面策略中的一种：

    - `Allow`（默认）：允许并发运行 Job
    - `Forbid`：禁止并发运行，如果前一个还没有完成，则直接跳过下一个
    - `Replace`：取消当前正在运行的 Job，用一个新的来替换

    `注意`，当前策略只能应用于同一个 Cron Job 创建的 Job。如果存在多个 Cron Job，它们创建的 Job 之间总是允许并发运行。

- 挂起

    `.spec.suspend` 字段也是可选的。如果设置为 `true`，后续所有执行都将被挂起。它对已经开始执行的 `Job` 不起作用。默认值为 `false`。

- 重启策略

    `restartPolicy` 仅支持 `Never` 或 `OnFailure`

## 参考链接
> https://kubernetes.io/zh/docs/concepts/workloads/controllers/cron-jobs/