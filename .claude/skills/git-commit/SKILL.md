# Git Commit Skill

## 规范

修改后的遵循 Angular 提交规范的英文版 Git Commit Comments (English)：

```Text
<type>(<scope>): git-emoji <subject>
<BLANK LINE>
<body>（Provide a detailed explanation of the reasons, logic, and impact of the modification）
<BLANK LINE>
<footer>（Associate issues, close bugs, etc., such as "Fixes # 123"）
```

## commit & push

commit 后

检查： 是否直接提交

### Yes

选择 Yes，表示我没有修改。可以直接 push

### No

选择 No，表示我修改了内容

则重新 commit，review code ，优先检查 新增文件是否 没有把隐私信息 ignore 我修改为 ignore 了

修改后 检查 commit，之后 push 到 remote
