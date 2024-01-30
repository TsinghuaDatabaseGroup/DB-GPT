import {Group} from 'butterfly-dag';
import $ from 'jquery';
import _ from 'lodash';

class BaseGroup extends Group {
  draw(obj) {
    let _dom = obj.dom;
    if (!_dom) {
      _dom = $('<div></div>')
        .attr('class', 'test_group')
        .css('top', obj.top)
        .css('left', obj.left)
        .attr('id', obj.id);
    }
    const group = $(_dom);
    this._container = $('<div></div>')
      .attr('class', 'test_container');

    group.append(this._container);

    // 添加文字
    if (_.get(obj, 'options.text')) {
      group.append(`<span class="text">${obj.options.text}</span>`);
    }

    return _dom;
  }
  getWidth() {
    return $(this.dom).width();
  }
  getHeight() {
    return $(this.dom).height();
  }
}

export default BaseGroup;
