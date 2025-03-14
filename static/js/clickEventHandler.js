$(document).ready(function () {
    // 初始加载
    loadChats();
    selectChat(currentChatId);

    // 发送摘要
    $("#send-btn").click(function () {
        sendMessage();
    });

    // 新建任务 - 使用事件委托绑定到父元素
    $(".chat-list").on("click", "#newchat", function () {
        let name = prompt("请输入任务名称", "新任务");
        if (name) newChat(name);
    });

    // 切换任务
    $(".chat-list").on("click", ".chat-item", function () {
        let chatId = $(this).data("id");
        selectChat(chatId);
    });

    // Enter 键发送
    $("#textarea").keypress(function (e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 复制功能
    $(".content").on("mouseenter", ".user-message, .assistant-message", function () {
        $("#menu").css({
            display: "block",
            top: $(this).position().top + "px",
            left: $(this).position().left + $(this).outerWidth() + "px"
        });
        $("#copy-btn").off("click").on("click", function () {
            navigator.clipboard.writeText($(this).parent().prev().text());
        });
    }).on("mouseleave", function () {
        $("#menu").hide();
    });
});