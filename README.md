# Trapper Script

## 在PRTS的使用方法
启用IPE后在你的`用户:xx/common.js`页加入以下代码：

```javascript
mw.loader.load('/index.php?title=User:GuBot/trapper.js&action=raw&ctype=text/javascript');
```

## 导出requirements
```
pdm update --unconstrained
pdm export -o requirements.txt --without-hashes
```
