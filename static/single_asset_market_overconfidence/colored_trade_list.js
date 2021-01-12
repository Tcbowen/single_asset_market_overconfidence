import { html } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import {TradeList} from '/static/otree_markets/trade_list.js';

import '/static/otree-redwood/src/otree-constants/otree-constants.js';


class ColoredTradeList extends TradeList{


	static get template() {
        return html`
            <style>
                #container {
                    width: 100%;
                    height: 100%;
                    overflow-y: auto;
                    box-sizing: border-box;
                }
                .my-trade {
	                background-color: #AA0011;
	            }
                #container div {
                    border: 1px solid black;
                    text-align: center;
                    margin: 3px;
                }
            </style>

            <otree-constants
                id="constants"
            ></otree-constants>

            <div id="container">
                <template is="dom-repeat" items="{{trades}}" as="trade" filter="{{_getAssetFilterFunc(assetName)}}">
                    <template is="dom-repeat" items="{{trade.making_orders}}" as="making_order">
                        <div class$="[[_getTradeClass(trade)]]">
                            <span>[[displayFormat(making_order, trade.taking_order)]]</span>
                        </div>
                    </template>
                </template>
            </div>
        `;
    }
    
    ready() {
        super.ready();
        this.pcode = this.$.constants.participantCode;
    }
   	_getTradeClass(trade) {
        if (trade.taking_order.pcode == this.pcode || trade.making_orders.some(order => order.pcode == this.pcode))
            return 'my-trade';
        else
            return 'other-trade';
    }
 }
 window.customElements.define('colored-trade-list', ColoredTradeList);
