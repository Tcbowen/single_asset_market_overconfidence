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
                .my-trade-buy {
	                background-color: #3EF849;
	            }
                .my-trade-sell {
                    background-color: #00FDF5;
                }
                .other-trade{
                     background-color: None;
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
        // for traking order
            if (trade.taking_order.pcode == this.pcode){
                if(trade.taking_order.is_bid)
                    return 'my-trade-buy';
                else
                    return 'my-trade-sell';
            }
        // for making order
            else if  (trade.making_orders.some(order => order.pcode == this.pcode)){
                var order;
                for (var i = 0; i < trade.making_orders.length; i++) {
                    if (trade.making_orders[i].pcode == this.pcode)
                        order = trade.making_orders[i];
                }
                if(order.is_bid)
                    return 'my-trade-buy';
                else
                    return 'my-trade-sell';
            }
        //for other orders
            else {
                return "other-trade";
            }
        }
 }
 window.customElements.define('colored-trade-list', ColoredTradeList);
