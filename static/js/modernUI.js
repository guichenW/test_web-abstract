/**
 * 现代化UI交互增强脚本
 * 为文本摘要工具添加动画效果和交互优化
 */

// 页面加载完成后执行
$(document).ready(function() {
    // 为新消息添加动画效果
    function enhanceUIWithAnimations() {
        // 监听DOM变化，为新添加的消息添加动画
        const contentObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    $(mutation.addedNodes).each(function() {
                        if ($(this).hasClass('item')) {
                            $(this).addClass('fade-in');
                            $(this).find('.bubble').addClass('slide-up');
                        }
                    });
                }
            });
        });
        
        // 开始观察内容区域的变化
        contentObserver.observe($('.content')[0], {
            childList: true,
            subtree: true
        });
    }
    
    // 改进任务列表项的交互
    function enhanceChatListInteraction() {
        // 为任务列表项添加悬停效果
        $(document).on('mouseenter', '.chat-item', function() {
            $(this).css('transform', 'translateY(-2px)');
        });
        
        $(document).on('mouseleave', '.chat-item', function() {
            $(this).css('transform', 'translateY(0)');
        });
        
        // 点击任务列表项时添加选中动画
        $(document).on('click', '.chat-item', function() {
            $('.chat-item').removeClass('selected');
            $(this).addClass('selected');
        });
    }
    
    // 改进输入区域交互
    function enhanceInputAreaInteraction() {
        // 输入框获得焦点时的效果
        $('#textarea').on('focus', function() {
            $(this).parent().css('box-shadow', '0 0 0 3px rgba(74, 111, 165, 0.2)');
        });
        
        $('#textarea').on('blur', function() {
            $(this).parent().css('box-shadow', 'none');
        });
        
        // 发送按钮交互效果
        $('#send-btn').on('mousedown', function() {
            $(this).css('transform', 'scale(0.95)');
        });
        
        $('#send-btn').on('mouseup mouseleave', function() {
            $(this).css('transform', 'scale(1)');
        });
    }
    
    // 添加响应式布局支持
    function enhanceResponsiveLayout() {
        // 检测窗口大小变化
        $(window).on('resize', function() {
            adjustLayout();
        });
        
        function adjustLayout() {
            const windowWidth = $(window).width();
            
            if (windowWidth <= 480) {
                // 手机设备布局调整 - 左侧容器默认隐藏
                // 不再设置高度和顺序，因为这些已经在CSS中设置
                $('.right-container').css({
                    'height': '100vh',
                    'min-height': '100vh'
                });
                // 优化触摸区域
                $('.button-area button').css('min-height', '44px');
                $('.chat-item, .newchat').css('min-height', '44px');
            } else if (windowWidth <= 768) {
                // 平板设备布局调整
                $('.left-container').css({
                    'height': '180px',
                    'min-height': 'auto'
                });
                $('.right-container').css({
                    'height': 'calc(95vh - 200px)',
                    'min-height': '400px'
                });
                // 恢复正常触摸区域
                $('.button-area button').css('min-height', '');
                $('.chat-item, .newchat').css('min-height', '');
            } else {
                // 恢复桌面布局
                $('.left-container').css({
                    'height': 'inherit',
                    'min-height': '500px'
                });
                $('.right-container').css({
                    'height': 'inherit',
                    'min-height': '500px'
                });
                // 恢复正常触摸区域
                $('.button-area button').css('min-height', '');
                $('.chat-item, .newchat').css('min-height', '');
            }
        }
        
        // 初始调整
        adjustLayout();
        
        // 添加触摸事件优化
        if ('ontouchstart' in window) {
            // 为按钮添加触摸反馈
            $('.button-area button, .head-btn, .chat-item, .newchat').on('touchstart', function() {
                $(this).addClass('touch-active');
            }).on('touchend touchcancel', function() {
                $(this).removeClass('touch-active');
            });
        }
    }
    
    // 初始化所有增强功能
    function initEnhancements() {
        enhanceUIWithAnimations();
        enhanceChatListInteraction();
        enhanceInputAreaInteraction();
        enhanceResponsiveLayout();
        
        // 页面加载完成后的初始动画
        $('.all-container').css('opacity', '0').animate({
            opacity: 1
        }, 500);
    }
    
    // 执行初始化
    initEnhancements();
});