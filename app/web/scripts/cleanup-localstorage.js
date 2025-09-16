// 清除损坏的聊天记录数据的脚本
// 在浏览器控制台中运行此代码来清除可能损坏的数据

console.log('开始清理聊天记录数据...');

// 清除聊天消息
const oldMessages = localStorage.getItem('chat_messages');
if (oldMessages) {
  console.log('找到旧的聊天记录:', oldMessages);
  localStorage.removeItem('chat_messages');
  console.log('已清除 chat_messages');
}

// 清除聊天历史
const oldHistory = localStorage.getItem('chat_history');
if (oldHistory) {
  console.log('找到旧的聊天历史:', oldHistory);
  localStorage.removeItem('chat_history');
  console.log('已清除 chat_history');
}

console.log('数据清理完成，请刷新页面！');