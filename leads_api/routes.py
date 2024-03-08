def includeme(config):
    # V1
    config.add_route(
        'v1_buyers_tiers_coverage',
        '/v1/buyers_tiers/{buyer_tier_slug}/coverage',
    )
