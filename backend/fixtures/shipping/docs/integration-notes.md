# 运费计算器集成说明

调用方依赖以下公共函数，函数名、参数顺序和默认值都不能改变：

```python
calculate_shipping_fee(subtotal_cents, destination, is_member=False)
```

- `subtotal_cents` 是整数分。
- `destination` 只使用 `"domestic"` 或 `"international"`。
- 返回值也是整数分，`0` 表示免运费。
