(function($){
    if (!String.prototype.trim) {
        String.prototype.trim = function () {
            return this.replace(/^[\s\xA0]+|[\s\xA0]+$/g, '');
        };
    }

    var header;
    var footer;

    var feeds;
    var feeds_container;
    var feeds_data;
    var feeds_selected_container;
    var feeds_selected;

    var feeds_selected_scroll = function(){
        if(!feeds_selected.is(':visible'))
        {
            return;
        }
        var feeds_data_top = feeds_data.offset().top;
        var feeds_data_bottom = feeds_data_top + feeds_data.height();

        var ele_width = feeds_selected_container.outerWidth(true);
        var ele_bottom = feeds_selected_container.offset().top + feeds_selected_container.height();

        var header_height = header.outerHeight();
        var window_top = $(window).scrollTop() + header_height;
        var window_bottom = footer.offset().top;

        if(feeds_data_top < window_top)
        {
            if(feeds_data_bottom < window_bottom)
            {
                feeds_selected_container.css({
                    position: 'absolute',
                    top: 'auto',
                    bottom: 0,
                    right: '',
                    left: ''
                });
            }
            else
            {
                var left = (feeds.offset().left + feeds.outerWidth()) - ele_width;
                feeds_selected_container.css({
                    position: 'fixed',
                    top: header_height,
                    bottom: 'auto',
                    right: '',
                    left: left
                });
            }
        }
        else
        {
            feeds_selected_container.css({
                position: '',
                top: '',
                bottom: '',
                left: '',
                right: ''
            });
        }
    }

    var handle_selected_feeds_height = function()
    {
        var window_h = $(window).height();
        var header_h = header.outerHeight();
        var footer_h = footer.outerHeight();
        feeds_selected_container.height(window_h - (header_h + footer_h));
    }

    var select_item = function()
    {
        var selected = $(this);
        selected.addClass('feeds-data-item-selected')
            .find('.feeds-data-select input')
                .prop('checked', true)
        ;

        var text = selected.find('.feeds-data-title').text().trim();
        var item = $('<li/>', { 'class': 'feeds-selected-item', text: text })
            .attr('data-item-num', selected.attr('data-item-num'))
        ;
        var remove = $('<span/>', { 'class': 'feeds-selected-remove'});
        item.append(remove);

        feeds_selected.append(item);

        feeds_container.addClass('feeds-has-selection');
        if(feeds_selected.children().length == 1)
        {
            feeds_selected_scroll();
        }
    }
    var unselect_item = function()
    {
        var unselected = $(this);
        unselected.removeClass('feeds-data-item-selected')
            .find('.feeds-data-select input')
                .prop('checked', false)
        ;

        var num = unselected.attr('data-item-num');
        var selector = '.feeds-selected-item[data-item-num="' + num + '"]';
        feeds_selected.find(selector).remove();
        if(!feeds_selected.children().length)
        {
            feeds_container.removeClass('feeds-has-selection');
        }
    }

    var return_selected_feeds = function(e)
    {
        if(!window.opener)
        {
            return false;
        }
        var feed_info = [];
        feeds_data.find('.feeds-data-item-selected').each(function(){
            var selected = $(this);
            var data = {
                title: selected.find('.feeds-data-title').text().trim(),
                url: selected.find('.feeds-data-title a').attr('href').trim(),
                subheader: selected.find('.feeds-data-subheader').text().trim(),
                partner: selected.find('.feeds-data-partner').text().trim(),
                author: selected.find('.feeds-data-author').text().trim(),
                date: selected.find('.feeds-data-date').text().trim()
            }
            feed_info.push(data);
        });
        window.opener.Govexec.handle_feeds(feed_info);
        window.close();
    }

    var apply_event_listeners = function()
    {
        var select_all = '.feeds-select-all input[type="checkbox"]';
        feeds.on('click', select_all, function(e){
            var target = $(this);

            var data_items;
            if(target.is(':checked'))
            {
                data_items = 'tbody :not(.feeds-data-item-selected).feeds-data-item';
                feeds.find(data_items).each(select_item);
            }
            else
            {
                data_items = 'tbody .feeds-data-item.feeds-data-item-selected';
                feeds.find(data_items).each(unselect_item);
            }
        });

        var select = 'tbody .feeds-data-item .feeds-data-select input[type="checkbox"]';
        feeds.on('click', select, function(){
            var target = $(this);
            if(target.is(':checked'))
            {
                target.closest('.feeds-data-item').each(select_item);
            }
            else
            {
                target.closest('.feeds-data-item').each(unselect_item);
            }
        });

        feeds_selected_container.on('click', '.feeds-selected-remove', function(){
            var item_num = $(this).parent().attr('data-item-num');
            feeds_data.find('[data-item-num="' + item_num + '"]').each(unselect_item);
        });

        $('.feeds-select-button').on('click', return_selected_feeds);


        $(window).scroll(feeds_selected_scroll);
    }

    $(window).resize(handle_selected_feeds_height);

    $(document).ready(function(){
        header = $('#header-container');
        footer = $('#footer');

        feeds = $('.feeds');
        feeds_container = feeds.find('.feeds-container');
        feeds_data = feeds.find('.feeds-data');
        feeds_selected_container = feeds.find('.feeds-selected-container');
        feeds_selected = feeds.find('.feeds-selected');

        handle_selected_feeds_height();
        apply_event_listeners();
    });
})(jQuery);
