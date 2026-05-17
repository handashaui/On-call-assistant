DOCUMENT_PROFILES: dict[str, str] = {
    "sop-001": "后端 服务 服务器挂了 服务器 挂了 宕机 不可用 超时 OOM 内存 降级 熔断 P0",
    "sop-002": "数据库 DBA MySQL Redis 主从 复制 延迟 慢查询 连接池 数据恢复",
    "sop-003": "前端 页面 白屏 浏览器 CDN 资源加载 JS 兼容性 性能劣化",
    "sop-004": "SRE 基础设施 服务器 挂了 Kubernetes K8s 集群 节点 不可用 故障 P0",
    "sop-005": "安全 黑客 攻击 入侵 漏洞 SQL注入 DDoS 恶意软件 数据泄露 威胁",
    "sop-006": "数据平台 ETL Spark Flink Kafka HDFS 数据管道 任务失败",
    "sop-007": "移动端 App 崩溃 热修复 推送 iOS Android OOM",
    "sop-008": "AI 算法 机器学习 模型 推荐 搜索排序 推理 GPU 效果下降 质量下降",
    "sop-009": "QA 测试 自动化 发版 测试环境 用例 流水线",
    "sop-010": "网络 CDN DNS DDoS 节点 负载均衡 带宽 解析 攻击",
}


def profile_for(doc_id: str) -> str:
    return DOCUMENT_PROFILES.get(doc_id, "")
