import { html, PolymerElement } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import '/static/otree-redwood/src/redwood-channel/redwood-channel.js';
import '/static/otree-redwood/src/otree-constants/otree-constants.js';

import '/static/otree_markets/trader_state.js'
import '/static/otree_markets/order_list.js';
import '/static/otree_markets/trade_list.js';
import '/static/otree_markets/simple_modal.js';
import '/static/otree_markets/event_log.js';

/*
    this component is a single-asset market, implemented using otree_markets' trader_state component and some of
    otree_markets' reusable UI widgets.
*/

class SingleAssetTextInterface extends PolymerElement {

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

                #log-container {
                    height: 20vh;
                }
                #log-container > div {
                    flex: 0 1 90%;
                }
                #container_orders > div {
                    height: 15vh;
                }
                order-list, trade-list, event-log {
                    border: 1px solid black;
                }
                .order-info-header {
                    text-align: center;
                    padding-bottom: 2px;
                }
                #allocation {
                    align-self: center;
                    text-align: center; 
                }   
                #order-input > div {
                    border: 1px solid black;
                    padding: 5px;
                    margin-bottom: 10px;
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
                settled-cash="{{settledCash}}"
                available-cash="{{availableCash}}"
                on-confirm-trade="_confirm_trade"
                on-confirm-cancel="_confirm_cancel"
                on-error="_handle_error"
            ></trader-state>
            <div class="container" id="main-container">
                <div>
                    <h3>Bids</h3>
                    <div class="order-info-header">
                        Price / Volume
                    </div>
                    <order-list
                        class="flex-fill"
                        display-format="[[ orderFormatter ]]"
                        orders="[[bids]]"
                        on-order-canceled="_order_canceled"
                        on-order-accepted="_order_accepted"
                    ></order-list>
                </div>
                <div>
                    <h3>Trades</h3>
                    <div class="order-info-header">
                        Price / Volume
                    </div>
                    <trade-list
                        class="flex-fill"
                        display-format="[[ tradeFormatter ]]"
                        trades="[[trades]]"
                    ></trade-list>
                </div>
                <div>
                    <h3>Asks</h3>
                    <div class="order-info-header">
                        Price / Volume
                    </div>
                    <order-list
                        class="flex-fill"
                        display-format="[[ orderFormatter ]]"
                        orders="[[asks]]"
                        on-order-canceled="_order_canceled"
                        on-order-accepted="_order_accepted"
                    ></order-list>
                </div>
                <div id="allocation">
                    <div>
                        <h4>Your Allocation</h4>
                    </div>
                    <div>Your Experimental Points: {{settledCash}}</div>
                    <div>Your Assets: {{settledAssets}}</div>
                </div>
            </div>
            <div class="container" id="order-input">
                <div>
                    <label for="bid_price_input">Price</label>
                    <input id="bid_price_input" type="number" min="0">
                    <label for="bid_volume_input">Volume</label>
                    <input id="bid_volume_input" type="number" min="1">
                    <div>
                        <button type="button" on-click="_order_entered" value="bid">Enter Bid</button>
                    </div>
                </div>
                <div>
                    <label for="ask_price_input">Price</label>
                    <input id="ask_price_input" type="number" min="0">
                    <label for="ask_volume_input">Volume</label>
                    <input id="ask_volume_input" type="number" min="1">
                    <div>
                        <button type="button" on-click="_order_entered" value="ask">Enter Ask</button>
                    </div>
                </div>
            </div>
            <div class="container" id="log-container">
                <div>
                    <event-log
                        class="flex-fill"
                        id="log"
                        max-entries=100
                    ></event-log>
                </div>
            </div>
        `;
    }

    ready() {
        super.ready();
        this.pcode = this.$.constants.participantCode;
        this.orderFormatter = order => {
            return `${order.price} / ${order.volume}`
        }
        this.tradeFormatter = trade => {
            return `${trade.taking_order.price} / ${trade.taking_order.traded_volume}`;
        };
    }

    // triggered when this player enters an order
    _order_entered(event) {
        const is_bid = event.target.value == 'bid';
        let price, volume;
        if (is_bid) {
            price = parseInt(this.$.bid_price_input.value);
            volume = parseInt(this.$.bid_volume_input.value);
        }
        else {
            price = parseInt(this.$.ask_price_input.value);
            volume = parseInt(this.$.ask_volume_input.value);
        }

        if (isNaN(price) || isNaN(volume)) {
            this.$.log.error('Invalid order entered');
            return;
        }
        this.$.trader_state.enter_order(price, volume, is_bid);
    }

    // triggered when this player cancels an order
    _order_canceled(event) {
        const order = event.detail;

        this.$.modal.modal_text = 'Are you sure you want to remove this order?';
        this.$.modal.on_close_callback = (accepted) => {
            if (!accepted)
                return;

            this.$.trader_state.cancel_order(order);
        };
        this.$.modal.show();
    }

    // triggered when this player accepts someone else's order
    _order_accepted(event) {
        const order = event.detail;
        if (order.pcode == this.pcode)
            return;

        this.$.modal.modal_text = `Do you want to ${order.is_bid ? 'buy' : 'sell'} for $${order.price}?`
        this.$.modal.on_close_callback = (accepted) => {
            if (!accepted)
                return;

            this.$.trader_state.accept_order(order);
        };
        this.$.modal.show();
    }

    // react to the backend confirming that a trade occurred
    _confirm_trade(event) {
        const trade = event.detail;
        const all_orders = trade.making_orders.concat([trade.taking_order]);
        for (let order of all_orders) {
            if (order.pcode == this.pcode)
                this.$.log.info(`You ${order.is_bid ? 'bought' : 'sold'} ${order.traded_volume} ${order.traded_volume == 1 ? 'unit' : 'units'}`);
        }
    }

    // react to the backend confirming that an order was canceled
    _confirm_cancel(event) {
        const order = event.detail;
        if (order.pcode == this.pcode) {
            this.$.log.info(`You canceled your ${msg.is_bid ? 'bid' : 'ask'}`);
        }
    }

    // handle an error sent from the backend
    _handle_error(event) {
        let message = event.detail;
        this.$.log.error(message)
    }
}

window.customElements.define('single-asset-text-interface', SingleAssetTextInterface);
