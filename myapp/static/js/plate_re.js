//用于plate_re.html页面的按钮事件绑定

// 退出登录按钮绑定事件
// 获取按钮元素
let logoutButton = document.getElementById('logoutButton');
// 为按钮添加点击事件处理
logoutButton.addEventListener('click', function () {
    // 重定向
    window.location.href = '/plate_re/logout';
});


// 展示识别数据按钮绑定事件
// 获取按钮元素
let displayButton = document.getElementById('displayButton');
// 为按钮添加点击事件处理
displayButton.addEventListener('click', function () {
    // 在新标签中打开页面
    window.open('/plate_re/plate_display', '_blank');
});