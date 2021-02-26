import { html } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import {OrderList} from '/static/otree_markets/order_list.js';

class ColoredOrderList extends OrderList{


	static get template() {
		 return html`
		 <style>
                #container {
                    width: 100%;
                    height: 100%;
                    overflow-y: auto;
                    box-sizing: border-box;
                }
                .my-bid-order {
	                background-color: #3EF849;
	            }
                .my-ask-order {
                    background-color: #00FDF5;
                }
                #container > div {
                    position: relative;
                    border: 1px solid black;
                    text-align: center;
                    margin: 3px;
                    cursor: default;
                    user-select: none;
                }
                .cancel-button {
                    position: absolute;
                    color: red;
                    line-height: 0.85;
                    height: 100%;
                    right: 10px;
                    font-size: 150%;
                    cursor: pointer;
                    user-select: none;
                }
                .other-order .cancel-button {
                    display: none;
                }
            </style>

            <otree-constants
                id="constants"
            ></otree-constants>

            <div id="container">
                <template is="dom-repeat" items="{{orders}}" filter="{{_getAssetFilterFunc(assetName)}}">
                    <div on-dblclick="_acceptOrder" class$="[[_getOrderClass(item)]]">
                        <span>[[displayFormat(item)]]</span>
                        <span class="cancel-button" on-click="_cancelOrder">&#9746;</span>
                    </div>
                </template>
            </div>
	            `;
	    }

        _getOrderClass(order) {
        if (order.pcode == this.pcode)
            if (order.is_bid)
                return 'my-bid-order';
            else
                return 'my-ask-order'
        else
            return 'other-order';
    }
}

window.customElements.define('colored-order-list', ColoredOrderList);