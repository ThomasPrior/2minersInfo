#!/usr/bin/env python3

import requests
import voluptuous as vol
from datetime import datetime, date, timedelta
import urllib.error

from .const import (
    _LOGGER,
    CONF_CURRENCY_NAME,
    CONF_ID,
    CONF_MINER_ADDRESS,
    CONF_UPDATE_FREQUENCY,
    CONF_NAME_OVERRIDE,
    CONF_TOKEN,
    CONF_SOLO,
    SENSOR_PREFIX,
    BTG_API_ENDPOINT,
    SOLO_BTG_API_ENDPOINT,
    ZEC_API_ENDPOINT,
    SOLO_ZEC_API_ENDPOINT,
    ZEN_API_ENDPOINT,
    SOLO_ZEN_API_ENDPOINT,
    ETH_API_ENDPOINT,
    SOLO_ETH_API_ENDPOINT,
    ERG_API_ENDPOINT,
    SOLO_ERG_API_ENDPOINT,
    ETC_API_ENDPOINT,
    SOLO_ETC_API_ENDPOINT,
    EXP_API_ENDPOINT,
    SOLO_EXP_API_ENDPOINT,
    ETP_API_ENDPOINT,
    SOLO_ETP_API_ENDPOINT,
    CLO_API_ENDPOINT,
    SOLO_CLO_API_ENDPOINT,
    XMR_API_ENDPOINT,
    SOLO_XMR_API_ENDPOINT,
    XZC_API_ENDPOINT,
    SOLO_XZC_API_ENDPOINT,
    ZEL_API_ENDPOINT,
    SOLO_ZEL_API_ENDPOINT,
    GRIN_API_ENDPOINT,
    SOLO_GRIN_API_ENDPOINT,
    MWC_API_ENDPOINT,
    SOLO_MWC_API_ENDPOINT,
    RVC_API_ENDPOINT,
    SOLO_RVC_API_ENDPOINT,
    AE_API_ENDPOINT,
    SOLO_AE_API_ENDPOINT,
    BEAM_API_ENDPOINT,
    SOLO_BEAM_API_ENDPOINT,
    CTXC_API_ENDPOINT,
    SOLO_CTXC_API_ENDPOINT,
    CKB_API_ENDPOINT,
    SOLO_CKB_API_ENDPOINT,
    COINGECKO_API_ENDPOINT,
    COINGECKO_API_CURRENCY,
    ATTR_ACTIVE_WORKERS,
    ATTR_CURRENT_HASHRATE,
    ATTR_INVALID_SHARES,
    ATTR_LAST_UPDATE,
    ATTR_REPORTED_HASHRATE,
    ATTR_STALE_SHARES,
    ATTR_UNPAID,
    ATTR_VALID_SHARES,
    ATTR_START_BLOCK,
    ATTR_END_BLOCK,
    ATTR_AMOUNT,
    ATTR_TXHASH,
    ATTR_PAID_ON,
    ATTR_AVERAGE_HASHRATE_24h,
    ATTR_SINGLE_COIN_LOCAL_CURRENCY,
    ATTR_TOTAL_UNPAID_LOCAL_CURRENCY,
    ATTR_COINS_PER_MINUTE,
    ATTR_CURRENT_HASHRATE_MH_SEC,
    ATTR_TOKEN_NAME
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCES
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MINER_ADDRESS): cv.string,
        vol.Required(CONF_UPDATE_FREQUENCY, default=1): cv.string,
        vol.Required(CONF_CURRENCY_NAME, default="usd"): cv.string,
        vol.Optional(CONF_ID, default=""): cv.string,
        vol.Optional(CONF_NAME_OVERRIDE, default=""): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_SOLO): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup 2minersInfo sensor")

    id_name = config.get(CONF_ID)
    miner_address = config.get(CONF_MINER_ADDRESS).strip()
    local_currency = config.get(CONF_CURRENCY_NAME).strip().lower()
    token = config.get(CONF_TOKEN).strip().lower()
    update_frequency = timedelta(minutes=(int(config.get(CONF_UPDATE_FREQUENCY))))
    name_override = config.get(CONF_NAME_OVERRIDE).strip()
    solo = config.get(CONF_SOLO).lower()

    entities = []

    try:
        entities.append(
            InfoSensor(
                miner_address, local_currency, token, update_frequency, id_name, name_override, solo
            )
        )
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    add_entities(entities)


class InfoSensor(Entity):
    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        return {ATTR_ACTIVE_WORKERS: self._active_workers, ATTR_CURRENT_HASHRATE: self._current_hashrate,
                ATTR_LAST_UPDATE: self._last_update, ATTR_UNPAID: self._unpaid, ATTR_AMOUNT: self._amount,
                ATTR_TXHASH: self._txhash, ATTR_PAID_ON: self._paid_on,
                ATTR_SINGLE_COIN_LOCAL_CURRENCY: self._single_coin_in_local_currency,
                ATTR_TOTAL_UNPAID_LOCAL_CURRENCY: self._unpaid_in_local_currency,
                ATTR_CURRENT_HASHRATE_MH_SEC: self._current_hashrate_mh_sec
                }

    def __init__(
            self, miner_address, local_currency, token, update_frequency, id_name, name_override, solo
    ):
        self.data = None
        self.miner_address = miner_address
        self.local_currency = local_currency
        self.token = token
        self.token_name = None
        self.update = Throttle(update_frequency)(self._update)
        self.solo = solo

        self._state = None
        self._active_workers = None
        self._current_hashrate = None
        self._last_update = None
        self._unpaid = None
        self._unit_of_measurement = "\u200b"
        self._amount = None
        self._txhash = None
        self._paid_on = None
        self._single_coin_in_local_currency = None
        self._unpaid_in_local_currency = None
        self._current_hashrate_mh_sec = None

        if name_override:
            self._name = SENSOR_PREFIX + name_override
        else:
            self._name = SENSOR_PREFIX + (id_name + " " if len(id_name) > 0 else "") + miner_address

        if self.token.lower() == "ae":
            self._icon = "mdi:infinity"
            self.token_name = "aeternity"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_AE_API_ENDPOINT
            else:
              self.api_endpoint = AE_API_ENDPOINT
        if self.token.lower() == "beam":
            self._icon = "mdi:triangle"
            self.token_name = "beam"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_BEAM_API_ENDPOINT
            else:
              self.api_endpoint = BEAM_API_ENDPOINT
        if self.token.lower() == "btg":
            self._icon = "mdi:bitcoin"
            self.token_name = "bitcoin-gold"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_BTG_API_ENDPOINT
            else:
              self.api_endpoint = BTG_API_ENDPOINT
        if self.token.lower() == "ckb":
            self._icon = "mdi:alpha-n"
            self.token_name = "nervos-netowrk"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_BTG_API_ENDPOINT
            else:
              self.api_endpoint = BTG_API_ENDPOINT
        if self.token.lower() == "clo":
            self._icon = "mdi:play"
            self.token_name = "callisto-network"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_CLO_API_ENDPOINT
            else:
              self.api_endpoint = CLO_API_ENDPOINT
        if self.token.lower() == "ctxc":
            self._icon = "mdi:triangle"
            self.token_name = "cortex"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_CTXC_API_ENDPOINT
            else:
              self.api_endpoint = CTXC_API_ENDPOINT
        if self.token.lower() == "etc":
            self._icon = "mdi:ethereum"
            self.token_name = "ethereum-classic"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ETC_API_ENDPOINT
            else:
              self.api_endpoint = ETC_API_ENDPOINT
        if self.token.lower() == "eth":
            self._icon = "mdi:ethereum"
            self.token_name = "ethereum"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ETH_API_ENDPOINT
            else:
              self.api_endpoint = ETH_API_ENDPOINT        
        if self.token.lower() == "erg":
            self._icon = "mdi:diamond"
            self.token_name = "ergo"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ERG_API_ENDPOINT
            else:
              self.api_endpoint = ERG_API_ENDPOINT
        if self.token.lower() == "etp":
            self._icon = "mdi:alpha-m"
            self.token_name = "metaverse-etp"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ETP_API_ENDPOINT
            else:
              self.api_endpoint = ETP_API_ENDPOINT
        if self.token.lower() == "exp":
            self._icon = "mdi:hexagon"
            self.token_name = "expanse"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_EXP_API_ENDPOINT
            else:
              self.api_endpoint = EXP_API_ENDPOINT
        if self.token.lower() == "grin":
            self._icon = "mdi:emoticon-happy-outline"
            self.token_name = "grin"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_GRIN_API_ENDPOINT
            else:
              self.api_endpoint = GRIN_API_ENDPOINT
        if self.token.lower() == "mwc":
            self._icon = "mdi:rhombus"
            self.token_name = "mimblewimblecoin"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_MWC_API_ENDPOINT
            else:
              self.api_endpoint = MWC_API_ENDPOINT
        if self.token.lower() == "rvn":
            self._icon = "mdi:bird"
            self.token_name = "ravencoin"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_RVC_API_ENDPOINT
            else:
              self.api_endpoint = RVC_API_ENDPOINT
        if self.token.lower() == "xmr":
            self._icon = "mdi:alpha-m-circle"
            self.token_name = "monero"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_XMR_API_ENDPOINT
            else:
              self.api_endpoint = XMR_API_ENDPOINT
        if self.token.lower() == "xzc":
            self._icon = "mdi:alpha-z-circle"
            self.token_name = "firo"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_XZC_API_ENDPOINT
            else:
              self.api_endpoint = XZC_API_ENDPOINT
        if self.token.lower() == "zec":
            self._icon = "mdi:alpha-z-circle"
            self.token_name = "zcash"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ZEC_API_ENDPOINT
            else:
              self.api_endpoint = ZEC_API_ENDPOINT
        if self.token.lower() == "zel":
            self._icon = "mdi:hexagon"
            self.token_name = "flux"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ZEL_API_ENDPOINT
            else:
              self.api_endpoint = ZEL_API_ENDPOINT
        if self.token.lower() == "zen":
            self._icon = "mdi:alpha-z-circle"
            self.token_name = "horizen"
            if self.solo.lower() == "true":
              self.api_endpoint = SOLO_ZEN_API_ENDPOINT
            else:
              self.api_endpoint = ZEN_API_ENDPOINT

    def _update(self):
        walleturl = (
                self.api_endpoint
                + "/accounts/"
                + self.miner_address
        )
        coingeckourl = (
                COINGECKO_API_ENDPOINT
                + self.token_name
                + COINGECKO_API_CURRENCY
                + self.local_currency
        )

        # sending get request to 2miners dashboard endpoint
        r = requests.get(walleturl).json()
        # extracting response json
        self.data = r
        walleturldata = self.data

        # sending get request to Congecko API endpoint
        r2 = requests.get(url=coingeckourl).json()
        # extracting response json
        self.data2 = r2
        coingeckodata = self.data2

        try:
            if len(r) == 0:
                raise ValueError()
            if len(r) >= 1:
                self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
                self._state = r['workersOnline']
                self._active_workers = r['workersOnline']
                self._current_hashrate = r['currentHashrate']
                self._unpaid = r['stats']['balance']
                self._paid_on = datetime.fromtimestamp(int(r['payments'][0]['timestamp'])).strftime('%d-%m-%Y %H:%M')
                calculate_hashrate_mh_sec = self._current_hashrate / 1000000
                self._current_hashrate_mh_sec = round(calculate_hashrate_mh_sec, 2)
                if len(r['payments']):
                  self._amount = r['payments'][0]['amount']
                  self._txhash = r['payments'][0]['tx']
                if len(r2[self.token_name]):
                    self._single_coin_in_local_currency = r2[self.token_name][self.local_currency]
                    calculate_unpaid = self._unpaid / 1000000000 * self._single_coin_in_local_currency
                    self._unpaid_in_local_currency = round(calculate_unpaid, 2)
            else:
                raise ValueError()

        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
