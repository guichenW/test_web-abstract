let currentChatId = "default";
let chats = {};

// 加载任务列表
function loadChats() {
    // 从服务器获取聊天列表
    $.ajax({
        url: "/chats",
        method: "GET",
        success: function(response) {
            if (response.ok && response.data) {
                // 清空现有列表
                $(".chat-list").empty();
                $(".chat-list").append('<div class="newchat" id="newchat">新建摘要任务</div>');
                
                // 如果没有聊天，创建默认聊天
                if (response.data.length === 0) {
                    chats = { "default": { name: "默认任务", messages: [] } };
                    // 创建默认聊天到服务器
                    $.ajax({
                        url: "/chats",
                        method: "POST",
                        contentType: "application/json",
                        data: JSON.stringify({ name: "默认任务" }),
                        success: function(resp) {
                            if (resp.ok && resp.data) {
                                currentChatId = resp.data.chat_id;
                            }
                        }
                    });
                } else {
                    // 更新本地聊天列表
                    chats = {};
                    response.data.forEach(chat => {
                        chats[chat.chat_id] = { name: chat.name, messages: [] };
                    });
                    
                    // 如果当前聊天ID不在列表中，设置为第一个聊天
                    if (!chats[currentChatId] && response.data.length > 0) {
                        currentChatId = response.data[0].chat_id;
                    }
                }
                
                // 渲染聊天列表
                for (let chatId in chats) {
                    let chat = chats[chatId];
                    let selected = chatId === currentChatId ? " selected" : "";
                    let html = `<div class="chat-item${selected}" data-id="${chatId}">${chat.name}</div>`;
                    $(".chat-list").append(html);
                }
                
                // 选择当前聊天
                selectChat(currentChatId);
            }
        },
        error: function() {
            console.error("获取聊天列表失败");
            // 使用默认聊天
            chats = { "default": { name: "默认任务", messages: [] } };
            $(".chat-list").empty();
            $(".chat-list").append('<div class="newchat" id="newchat">新建摘要任务</div>');
            let html = `<div class="chat-item selected" data-id="default">默认任务</div>`;
            $(".chat-list").append(html);
        }
    });
}

// 切换任务
function selectChat(chatId) {
    if (!chats[chatId]) return;
    currentChatId = chatId;
    
    // 更新UI
    $(".chat-list .chat-item").removeClass("selected");
    $(`.chat-list .chat-item[data-id="${chatId}"]`).addClass("selected");
    $(".head-chat-name").text(chats[chatId].name);
    $(".content").empty();
    
    // 从服务器获取聊天消息
    $.ajax({
        url: `/chats/${chatId}/messages`,
        method: "GET",
        success: function(response) {
            if (response.ok && response.data) {
                chats[chatId].messages = response.data;
                $(".head-chat-info").text(`共${chats[chatId].messages.length}条记录`);
                
                // 显示消息
                chats[chatId].messages.forEach(msg => {
                    let messageObj = {
                        role: msg.role,
                        content: msg.content,
                        send_time: msg.timestamp,
                        display_time: true
                    };
                    appendMessage(messageObj);
                });
            }
        },
        error: function() {
            console.error("获取聊天消息失败");
            $(".head-chat-info").text("获取消息失败");
        }
    });
}

// 创建新任务
function newChat(name) {
    // 创建新聊天到服务器
    $.ajax({
        url: "/chats",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ name: name }),
        success: function(response) {
            if (response.ok && response.data) {
                let chatId = response.data.chat_id;
                chats[chatId] = { name: name, messages: [] };
                selectChat(chatId);
                // 重新加载聊天列表
                loadChats();
            }
        },
        error: function() {
            console.error("创建新聊天失败")
        }
    });
}

// 修改任务名称
function updateChatName(chatId, newName) {
    // 更新聊天名称到服务器
    $.ajax({
        url: `/chats/${chatId}`,
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify({ name: newName }),
        success: function(response) {
            if (response.ok && response.data) {
                chats[chatId].name = newName;
                // 更新UI
                $(`.chat-list .chat-item[data-id="${chatId}"]`).text(newName);
                if (currentChatId === chatId) {
                    $(".head-chat-name").text(newName);
                }
            }
        },
        error: function() {
            console.error("更新聊天名称失败");
            alert("更新任务名称失败");
        }
    });
}

// 删除任务
function deleteChat(chatId) {
    if (!confirm("确定要删除这个任务吗？所有相关的消息也将被删除。")) {
        return;
    }
    
    // 删除聊天到服务器
    $.ajax({
        url: `/chats/${chatId}`,
        method: "DELETE",
        success: function(response) {
            if (response.ok) {
                delete chats[chatId];
                // 如果删除的是当前聊天，则选择第一个聊天或创建新聊天
                if (currentChatId === chatId) {
                    let chatIds = Object.keys(chats);
                    if (chatIds.length > 0) {
                        selectChat(chatIds[0]);
                    } else {
                        // 如果没有聊天了，创建一个默认聊天
                        newChat("默认任务");
                    }
                }
                // 重新加载聊天列表
                loadChats();
            }
        },
        error: function() {
            console.error("删除聊天失败");
            alert("删除任务失败");
        }
    });
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
        // 格式化时间显示
        let formattedTime = message.send_time;
        if (typeof get_time_str === 'function' && message.send_time) {
            try {
                formattedTime = get_time_str(new Date(message.send_time));
            } catch (e) {
                console.log("时间格式化失败", e);
            }
        }
        html = `<div class="item item-center"><span>${formattedTime}</span></div>` + html;
    }
    $(".content").append(html);
    hljs.highlightAll();
    $(".content").scrollTop($(".content")[0].scrollHeight);
}