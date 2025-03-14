let currentChatId = "default";
let chats = { "default": { name: "默认任务", messages: [] } };

// 加载任务列表
function loadChats() {
    $(".chat-list").empty();
    $(".chat-list").append('<div class="newchat" id="newchat">新建摘要任务</div>');
    for (let chatId in chats) {
        let chat = chats[chatId];
        let selected = chatId === currentChatId ? " selected" : "";
        let html = `<div class="chat-item${selected}" data-id="${chatId}">${chat.name}</div>`;
        $(".chat-list").append(html);
    }
}

// 切换任务
function selectChat(chatId) {
    if (!chats[chatId]) return;
    currentChatId = chatId;
    loadChats();
    $(".head-chat-name").text(chats[chatId].name);
    $(".head-chat-info").text(`共${chats[chatId].messages.length}条记录`);
    $(".content").empty();
    chats[chatId].messages.forEach(appendMessage);
}

// 创建新任务
function newChat(name) {
    let chatId = "chat-" + Date.now();
    chats[chatId] = { name: name, messages: [] };
    selectChat(chatId);
}

// 发送消息并获取摘要
function sendMessage() {
    var message = $("#textarea").val().trim();
    if (!message) {
        alert("请输入文本！");
        return;
    }

    var sendTime = new Date().toLocaleString();
    var messageObj = { role: "user", content: message, send_time: sendTime, display_time: true };
    chats[currentChatId].messages.push(messageObj);
    appendMessage(messageObj);
    $(".head-chat-info").text(`共${chats[currentChatId].messages.length}条记录`);
    $("#textarea").val("");

    $.ajax({
        url: "/abstract",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ text: message, chat_id: currentChatId }),
        complete: function (xhr, status) {
            console.log("AJAX 完成 - 状态码:", xhr.status, "响应:", xhr.responseText); // 调试信息
            let response = xhr.responseJSON || {};
            let result = { role: "assistant", content: "", send_time: new Date().toLocaleString(), display_time: true };
            if (xhr.status === 200 && response.ok) {
                result.content = response.data;
            } else {
                result.content = "错误: " + (response.errors || "未知错误 (状态码: " + xhr.status + ")");
            }
            chats[currentChatId].messages.push(result);
            appendMessage(result);
            $(".head-chat-info").text(`共${chats[currentChatId].messages.length}条记录`);
        }
        // 移除 error 回调，让 complete 处理所有情况
    });
}

// 显示消息
function appendMessage(message) {
    var content = marked.parse(message.content);
    var itemClass = message.role === "user" ? "item-right" : message.role === "assistant" ? "item-left" : "item-center";
    var bubbleClass = "bubble";
    var html = `
        <div class="item ${itemClass}">
            <div class="${bubbleClass}">${content}</div>
        </div>`;
    if (message.display_time) {
        html = `<div class="item item-center"><span>[${message.send_time}]</span></div>` + html;
    }
    $(".content").append(html);
    hljs.highlightAll();
    $(".content").scrollTop($(".content")[0].scrollHeight);
}