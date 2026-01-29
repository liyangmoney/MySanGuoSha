const express = require('express');
const app = express();
const PORT = 3000;

// 允许访问客户端静态文件
app.use(express.static('../client'));

// 示例接口
app.get('/api/hello', (req, res) => {
    res.json({ message: '欢迎来到《三国杀》服务端！' });
});

app.listen(PORT, () => {
    console.log(`服务器正在 http://localhost:${PORT} 上运行`);
});