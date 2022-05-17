# 2minersInfo

## A custom component for [HomeAssistant](https://github.com/home-assistant/core) 

Provides data from [2miners.com](https://2miners.com) on a specified miner.

If this has been of use, please consider funding my caffeine habit:

<a href="https://www.buymeacoffee.com/tomprior" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

# Functionality

* Create sensor items for cryptocurrency miners/worker machines using 2miners, either pooled or solo for supported coins.

Supported coins are as follows:

- Aeternity (ae)
- BEAM (beam)
- Bitvcoin Gold (btg)
- Cortex (ctxc)
- Ethereum Classic (etc)
- Ethereum (eth)
- Metaverse ETP (etp)
- Ergo (erg)
- Expanse (exp)
- Ravencoin (rvn)
- Monero (xmr)
- Zcash (zec)
- Flux (zel)


## Things you should know about 2minersInfo
* Use of the 2minersInfo API is subject to change - there may be occaisions where a code change is required before the component will work again.
* There are limits on how many requests can be made to 2minersInfo's API and therefore the data retrieved by 2minersInfo will be updated periodically and may be out of date by the time you look at it.
* Please do not use 2minersInfo in isolation to make decisions about your cryptocurrency holdings.
* 2minersInfo only reads the statistics of the provided miner.

## Pre-requisite knowledge

Before downloading and configuring 2minersInfo, please ensure you are familiar with the following items:

* HomeAssistant's configuration file [LINK](https://www.home-assistant.io/docs/configuration/)
* YAML syntax [LINK](https://www.home-assistant.io/docs/configuration/yaml/)
* Installation of custom components via:
  * HACS [LINK](https://hacs.xyz/docs/setup/prerequisites)
  * Manual custom component installation
* Adding template sensors to your configuration [LINK](https://www.home-assistant.io/integrations/template/)

## Installation

Copy the files in the /custom_components/2minersInfo/ folder to: [homeassistant]/config/custom_components/2minersInfo/

## Configuration

To use 2minersInfo, please add the following items to your HomeAssistant ```configuration.yaml```
````
sensor:
  - platform: 2minersinfo
    miner_address: (required) the address of your 2minersInfo miner
    currency_name: (required) the currency you would like your unpaid balance to be converted to 
    name_override: (optional) name to identify your wallet instead of your miner address.
    token: (required) the symbol of the token you are mining (eth, etc, rvn)
    solo: (required - whether you are a pooled miner (false) or solo miner (true)
````

Your wallet/miner address *must* be encapsulated in quote marks. Failure to do so will just return "unknown" in HomeAssistant.

Examples:

```
sensor:
  - platform: 2minersinfo
    miner_address: "0x1234567890123456789012345678901234567890"
    currency_name: USD
    token: eth
    solo: false
```

```
sensor:
  - platform: 2minersinfo
    miner_address: "0x1234567890123456789012345678901234567890"
    currency_name: USD
    token: etc
    solo: true
```

```
sensor:
  - platform: 2minersinfo
    miner_address: "1234567890123456789012345678901234567890"
    currency_name: CAD
    name_override: "wallet name"
    token: rvn
    solo: false
```

Multiple addresses can be configured.

## Templates

You can create a template sensor for any of the attributes returned by 2minersInfo. For example:

Current hashrate:
```{{ states.sensor.2minersinfo_miner_address.attributes['current_hashrate'] }}```

Unpaid amount:
```{{ states.sensor.2minersinfo_miner_address.attributes['unpaid'] }}```

## How does it look?

![image](https://user-images.githubusercontent.com/34111848/166410584-2ecddce7-d63b-4bca-825a-1d8de1170a2c.png)

![image](https://user-images.githubusercontent.com/34111848/166411766-410e2a42-e34f-4d58-8ddb-e10a3386af3e.png)


Some rather pretty graphs are possible with the [mini-graph-card](https://github.com/kalkih/mini-graph-card):

## Discussion

[Talk about 2minersInfo here](https://community.home-assistant.io/t/my-first-custom-component-2minersInfo/302734)

[Post issues with 2minersInfo here](https://github.com/ThomasPrior/2minersInfo/issues)

Issues should be posted with logs and relevant, redacted excerpts from your configuration.yaml file to ensure that help can be given most effectively.

Pull requests and constructive criticism are always welcome.

## Credits

[@heyajohnny's](https://github.com/heyajohnny) [CryptoInfo](https://github.com/heyajohnny/cryptoinfo) from which this component was born.

[W3Schools](https://www.w3schools.com/python/default.asp) for being an invaluable learning resource.
