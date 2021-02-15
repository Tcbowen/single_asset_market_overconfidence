import { html, PolymerElement } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import '/static/otree-redwood/src/redwood-channel/redwood-channel.js';
import '/static/otree-redwood/src/otree-constants/otree-constants.js';

import '/static/otree_markets/trader_state.js';
import './colored_trade_list.js';

/*
    this component is a single-asset market, implemented using otree_markets' trader_state component and some of
    otree_markets' reusable UI widgets.
*/

class TradeView extends PolymerElement {

    static get properties() {
        return {
            bids: Array,
            asks: Array,
            trades: Array,
            settledAssets: Number,
            availableAssets: Number,
            settledCash: Number,
            availableCash: Number,
        };
    }

    static get template() {
        return html`
            <style>
                .container {
                    display: flex;
                    justify-content: space-evenly;
                }
                .container > div {
                    display: flex;
                    flex-direction: column;
                }
                .flex-fill {
                    flex: 1 0 0;
                    min-height: 0;
                }
                #main-container {
                    height: 40vh;
                    margin-bottom: 10px;
                }
                #main-container > div {
                    flex: 0 1 20%;
                }
                colored-order-list, colored-trade-list, event-log {
                    border: 1px solid black;
                }
            </style>
            <simple-modal
                id="modal"
            ></simple-modal>
            <otree-constants
                id="constants"
            ></otree-constants>
            <trader-state
                id="trader_state"
                bids="{{bids}}"
                asks="{{asks}}"
                trades="{{trades}}"
                settled-assets="{{settledAssets}}"
                available-assets="{{availableAssets}}"
                settled-cash = "{{settledCash}}"
                available-cash="{{availableCash}}"
                on-confirm-trade="_confirm_trade"
                on-confirm-cancel="_confirm_cancel"
                on-error="_handle_error"
            ></trader-state>
            <div class="container" id="main-container">
                    <colored-trade-list
                        class="flex-fill"
                        display-format="[[ tradeFormatter ]]"
                        trades="[[trades]]"
                    ></colored-trade-list>
            </div>
        `;
    }

} 

window.customElements.define('trade-view', TradeView);
