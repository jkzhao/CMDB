from django.utils.safestring import mark_safe

class Page:
    def __init__(self, current_page, data_count, per_page_count=10, pager_num=7):
        self.current_page = current_page
        self.data_count = data_count #总共有多少数据
        self.per_page_count = per_page_count
        self.pager_num = pager_num #页面显示多少页码

    @property #加上这个就调用这个方法时就不用加()
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    @property
    def total_count(self):
        '计算总页数'
        v, y = divmod(self.data_count, self.per_page_count)
        if y:
            v += 1 #有余数，页数就+1页，否则不加
        if v == 0:
            v += 1 #如果data_count=0，v=0，即没有数据，页面最好也显示1页
        return v

    def page_str(self, base_url):
        '计算最后返回的page_str'
        page_list = []

        if self.total_count < self.pager_num:
            start_index = 1
            end_index = self.total_count + 1
        else:
            if self.current_page <= (self.pager_num + 1) / 2:
                start_index = 1
                end_index = self.pager_num + 1
            else:
                start_index = self.current_page - (self.pager_num - 1) / 2
                end_index = self.current_page + (self.pager_num + 1) / 2
                if (self.current_page + (self.pager_num - 1) / 2) > self.total_count:
                    end_index = self.total_count + 1
                    start_index = self.total_count - self.pager_num + 1

        if self.current_page == 1: #上一页
            prev = '<a class="page" href="javascript:void(0);">上一页</a>' #当 当前页是第1页的时候，点击上一页应该什么都不干
        else:
            prev = '<a class="page" href="%s?p=%s">上一页</a>' % (base_url, self.current_page - 1,)
        page_list.append(prev)

        for i in range(int(start_index), int(end_index)): #这样页面永远显示11个页码，选中的那个页面永远是最中间那个
            if i == self.current_page:
                temp = '<a class="page active" href="%s?p=%s">%s</a>' % (base_url, i, i)
            else:
                temp = '<a class="page" href="%s?p=%s">%s</a>' % (base_url, i, i)
        page_list.append(temp)

        if self.current_page == self.total_count: #下一页
            next = '<a class="page" href="javascript:void(0);">下一页</a>' #当 当前页是最后1页的时候，点击下一页应该什么都不干
        else:
            next = '<a class="page" href="%s?p=%s">下一页</a>' % (base_url, self.current_page + 1,)
        page_list.append(next)

        jump = """
        <input class="page_num" type='text' /> <a style="cursor: pointer;" onclick='jumpTo(this, "%s?p=");'>GO</a>
        <script>
            function jumpTo(ths,base){
                var val = ths.previousSibling.value;
                location.href = base + val;
            }
        </script>
        """ % (base_url,)

        page_list.append(jump)

        page_str = mark_safe("".join(page_list))

        return page_str
