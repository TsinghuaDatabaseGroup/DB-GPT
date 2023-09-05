# -*- coding: utf-8 -*-
# @Project: index_test
# @Module: constants
# @Author: Wei Zhou
# @Time: 2022/6/23 14:32

# todo: sepecified `tpch` or `tpcds` benchmark.
# TPC-H schema
tpch_tables = ["region", "nation", "supplier", "part", "customer", "orders", "partsupp", "lineitem"]
tpch_cols = ["r_regionkey", "r_name", "r_comment",
             "n_nationkey", "n_name", "n_regionkey", "n_comment",
             "s_suppkey", "s_name", "s_address", "s_nationkey", "s_phone", "s_acctbal", "s_comment",
             "p_partkey", "p_name", "p_mfgr", "p_brand", "p_type", "p_size", "p_container", "p_retailprice",
             "p_comment",
             "c_custkey", "c_name", "c_address", "c_nationkey", "c_phone", "c_acctbal", "c_mktsegment", "c_comment",
             "o_orderkey", "o_custkey", "o_orderstatus", "o_totalprice", "o_orderdate", "o_orderpriority", "o_clerk",
             "o_shippriority", "o_comment",
             "ps_partkey", "ps_suppkey", "ps_availqty", "ps_supplycost", "ps_comment",
             "l_orderkey", "l_partkey", "l_suppkey", "l_linenumber", "l_quantity", "l_extendedprice", "l_discount",
             "l_tax", "l_returnflag", "l_linestatus", "l_shipdate", "l_commitdate", "l_receiptdate", "l_shipinstruct",
             "l_shipmode", "l_comment"]
tpch_tbl_col = {"region": ["r_regionkey", "r_name", "r_comment"],
                "nation": ["n_nationkey", "n_name", "n_regionkey", "n_comment"],
                "supplier": ["s_suppkey", "s_name", "s_address", "s_nationkey", "s_phone", "s_acctbal", "s_comment"],
                "part": ["p_partkey", "p_name", "p_mfgr", "p_brand", "p_type",
                         "p_size", "p_container", "p_retailprice", "p_comment"],
                "customer": ["c_custkey", "c_name", "c_address", "c_nationkey", "c_phone",
                             "c_acctbal", "c_mktsegment", "c_comment"],
                "orders": ["o_orderkey", "o_custkey", "o_orderstatus", "o_totalprice", "o_orderdate",
                           "o_orderpriority", "o_clerk", "o_shippriority", "o_comment"],
                "partsupp": ["ps_partkey", "ps_suppkey", "ps_availqty", "ps_supplycost", "ps_comment"],
                "lineitem": ["l_orderkey", "l_partkey", "l_suppkey", "l_linenumber", "l_quantity", "l_extendedprice",
                             "l_discount", "l_tax", "l_returnflag", "l_linestatus", "l_shipdate", "l_commitdate",
                             "l_receiptdate", "l_shipinstruct", "l_shipmode", "l_comment"]}

# TPC-DS schema
tpcds_tables = ["dbgen_version", "warehouse", "promotion", "web_page", "item", "income_band", "time_dim",
                "catalog_page", "web_site", "ship_mode", "customer_address", "reason", "store", "customer_demographics",
                "store_returns", "catalog_sales", "inventory", "store_sales", "web_returns", "web_sales", "customer",
                "household_demographics", "catalog_returns", "call_center", "date_dim"]
tpcds_cols = ["dv_version", "dv_create_date", "dv_create_time", "dv_cmdline_args", "w_warehouse_sk", "w_warehouse_id",
              "w_warehouse_name", "w_warehouse_sq_ft", "w_street_number", "w_street_name", "w_street_type",
              "w_suite_number", "w_city", "w_county", "w_state", "w_zip", "w_country", "w_gmt_offset", "p_promo_sk",
              "p_promo_id", "p_start_date_sk", "p_end_date_sk", "p_item_sk", "p_cost", "p_response_target",
              "p_promo_name", "p_channel_dmail", "p_channel_email", "p_channel_catalog", "p_channel_tv",
              "p_channel_radio", "p_channel_press", "p_channel_event", "p_channel_demo", "p_channel_details",
              "p_purpose", "p_discount_active", "wp_web_page_sk", "wp_web_page_id", "wp_rec_start_date",
              "wp_rec_end_date", "wp_creation_date_sk", "wp_access_date_sk", "wp_autogen_flag", "wp_customer_sk",
              "wp_url", "wp_type", "wp_char_count", "wp_link_count", "wp_image_count", "wp_max_ad_count", "i_item_sk",
              "i_item_id", "i_rec_start_date", "i_rec_end_date", "i_item_desc", "i_current_price", "i_wholesale_cost",
              "i_brand_id", "i_brand", "i_class_id", "i_class", "i_category_id", "i_category", "i_manufact_id",
              "i_manufact", "i_size", "i_formulation", "i_color", "i_units", "i_container", "i_manager_id",
              "i_product_name", "ib_income_band_sk", "ib_lower_bound", "ib_upper_bound", "t_time_sk", "t_time_id",
              "t_time", "t_hour", "t_minute", "t_second", "t_am_pm", "t_shift", "t_sub_shift", "t_meal_time",
              "cp_catalog_page_sk", "cp_catalog_page_id", "cp_start_date_sk", "cp_end_date_sk", "cp_department",
              "cp_catalog_number", "cp_catalog_page_number", "cp_description", "cp_type", "web_site_sk", "web_site_id",
              "web_rec_start_date", "web_rec_end_date", "web_name", "web_open_date_sk", "web_close_date_sk",
              "web_class", "web_manager", "web_mkt_id", "web_mkt_class", "web_mkt_desc", "web_market_manager",
              "web_company_id", "web_company_name", "web_street_number", "web_street_name", "web_street_type",
              "web_suite_number", "web_city", "web_county", "web_state", "web_zip", "web_country", "web_gmt_offset",
              "web_tax_percentage", "sm_ship_mode_sk", "sm_ship_mode_id", "sm_type", "sm_code", "sm_carrier",
              "sm_contract", "ca_address_sk", "ca_address_id", "ca_street_number", "ca_street_name", "ca_street_type",
              "ca_suite_number", "ca_city", "ca_county", "ca_state", "ca_zip", "ca_country", "ca_gmt_offset",
              "ca_location_type", "r_reason_sk", "r_reason_id", "r_reason_desc", "s_store_sk", "s_store_id",
              "s_rec_start_date", "s_rec_end_date", "s_closed_date_sk", "s_store_name", "s_number_employees",
              "s_floor_space", "s_hours", "s_manager", "s_market_id", "s_geography_class", "s_market_desc",
              "s_market_manager", "s_division_id", "s_division_name", "s_company_id", "s_company_name",
              "s_street_number", "s_street_name", "s_street_type", "s_suite_number", "s_city", "s_county", "s_state",
              "s_zip", "s_country", "s_gmt_offset", "s_tax_precentage", "cd_demo_sk", "cd_gender", "cd_marital_status",
              "cd_education_status", "cd_purchase_estimate", "cd_credit_rating", "cd_dep_count",
              "cd_dep_employed_count", "cd_dep_college_count", "sr_returned_date_sk", "sr_return_time_sk", "sr_item_sk",
              "sr_customer_sk", "sr_cdemo_sk", "sr_hdemo_sk", "sr_addr_sk", "sr_store_sk", "sr_reason_sk",
              "sr_ticket_number", "sr_return_quantity", "sr_return_amt", "sr_return_tax", "sr_return_amt_inc_tax",
              "sr_fee", "sr_return_ship_cost", "sr_refunded_cash", "sr_reversed_charge", "sr_store_credit",
              "sr_net_loss", "cs_sold_date_sk", "cs_sold_time_sk", "cs_ship_date_sk", "cs_bill_customer_sk",
              "cs_bill_cdemo_sk", "cs_bill_hdemo_sk", "cs_bill_addr_sk", "cs_ship_customer_sk", "cs_ship_cdemo_sk",
              "cs_ship_hdemo_sk", "cs_ship_addr_sk", "cs_call_center_sk", "cs_catalog_page_sk", "cs_ship_mode_sk",
              "cs_warehouse_sk", "cs_item_sk", "cs_promo_sk", "cs_order_number", "cs_quantity", "cs_wholesale_cost",
              "cs_list_price", "cs_sales_price", "cs_ext_discount_amt", "cs_ext_sales_price", "cs_ext_wholesale_cost",
              "cs_ext_list_price", "cs_ext_tax", "cs_coupon_amt", "cs_ext_ship_cost", "cs_net_paid",
              "cs_net_paid_inc_tax", "cs_net_paid_inc_ship", "cs_net_paid_inc_ship_tax", "cs_net_profit", "inv_date_sk",
              "inv_item_sk", "inv_warehouse_sk", "inv_quantity_on_hand", "ss_sold_date_sk", "ss_sold_time_sk",
              "ss_item_sk", "ss_customer_sk", "ss_cdemo_sk", "ss_hdemo_sk", "ss_addr_sk", "ss_store_sk", "ss_promo_sk",
              "ss_ticket_number", "ss_quantity", "ss_wholesale_cost", "ss_list_price", "ss_sales_price",
              "ss_ext_discount_amt", "ss_ext_sales_price", "ss_ext_wholesale_cost", "ss_ext_list_price", "ss_ext_tax",
              "ss_coupon_amt", "ss_net_paid", "ss_net_paid_inc_tax", "ss_net_profit", "wr_returned_date_sk",
              "wr_returned_time_sk", "wr_item_sk", "wr_refunded_customer_sk", "wr_refunded_cdemo_sk",
              "wr_refunded_hdemo_sk", "wr_refunded_addr_sk", "wr_returning_customer_sk", "wr_returning_cdemo_sk",
              "wr_returning_hdemo_sk", "wr_returning_addr_sk", "wr_web_page_sk", "wr_reason_sk", "wr_order_number",
              "wr_return_quantity", "wr_return_amt", "wr_return_tax", "wr_return_amt_inc_tax", "wr_fee",
              "wr_return_ship_cost", "wr_refunded_cash", "wr_reversed_charge", "wr_account_credit", "wr_net_loss",
              "ws_sold_date_sk", "ws_sold_time_sk", "ws_ship_date_sk", "ws_item_sk", "ws_bill_customer_sk",
              "ws_bill_cdemo_sk", "ws_bill_hdemo_sk", "ws_bill_addr_sk", "ws_ship_customer_sk", "ws_ship_cdemo_sk",
              "ws_ship_hdemo_sk", "ws_ship_addr_sk", "ws_web_page_sk", "ws_web_site_sk", "ws_ship_mode_sk",
              "ws_warehouse_sk", "ws_promo_sk", "ws_order_number", "ws_quantity", "ws_wholesale_cost", "ws_list_price",
              "ws_sales_price", "ws_ext_discount_amt", "ws_ext_sales_price", "ws_ext_wholesale_cost",
              "ws_ext_list_price", "ws_ext_tax", "ws_coupon_amt", "ws_ext_ship_cost", "ws_net_paid",
              "ws_net_paid_inc_tax", "ws_net_paid_inc_ship", "ws_net_paid_inc_ship_tax", "ws_net_profit",
              "c_customer_sk", "c_customer_id", "c_current_cdemo_sk", "c_current_hdemo_sk", "c_current_addr_sk",
              "c_first_shipto_date_sk", "c_first_sales_date_sk", "c_salutation", "c_first_name", "c_last_name",
              "c_preferred_cust_flag", "c_birth_day", "c_birth_month", "c_birth_year", "c_birth_country", "c_login",
              "c_email_address", "c_last_review_date_sk", "hd_demo_sk", "hd_income_band_sk", "hd_buy_potential",
              "hd_dep_count", "hd_vehicle_count", "cr_returned_date_sk", "cr_returned_time_sk", "cr_item_sk",
              "cr_refunded_customer_sk", "cr_refunded_cdemo_sk", "cr_refunded_hdemo_sk", "cr_refunded_addr_sk",
              "cr_returning_customer_sk", "cr_returning_cdemo_sk", "cr_returning_hdemo_sk", "cr_returning_addr_sk",
              "cr_call_center_sk", "cr_catalog_page_sk", "cr_ship_mode_sk", "cr_warehouse_sk", "cr_reason_sk",
              "cr_order_number", "cr_return_quantity", "cr_return_amount", "cr_return_tax", "cr_return_amt_inc_tax",
              "cr_fee", "cr_return_ship_cost", "cr_refunded_cash", "cr_reversed_charge", "cr_store_credit",
              "cr_net_loss", "cc_call_center_sk", "cc_call_center_id", "cc_rec_start_date", "cc_rec_end_date",
              "cc_closed_date_sk", "cc_open_date_sk", "cc_name", "cc_class", "cc_employees", "cc_sq_ft", "cc_hours",
              "cc_manager", "cc_mkt_id", "cc_mkt_class", "cc_mkt_desc", "cc_market_manager", "cc_division",
              "cc_division_name", "cc_company", "cc_company_name", "cc_street_number", "cc_street_name",
              "cc_street_type", "cc_suite_number", "cc_city", "cc_county", "cc_state", "cc_zip", "cc_country",
              "cc_gmt_offset", "cc_tax_percentage", "d_date_sk", "d_date_id", "d_date", "d_month_seq", "d_week_seq",
              "d_quarter_seq", "d_year", "d_dow", "d_moy", "d_dom", "d_qoy", "d_fy_year", "d_fy_quarter_seq",
              "d_fy_week_seq", "d_day_name", "d_quarter_name", "d_holiday", "d_weekend", "d_following_holiday",
              "d_first_dom", "d_last_dom", "d_same_day_ly", "d_same_day_lq", "d_current_day", "d_current_week",
              "d_current_month", "d_current_quarter", "d_current_year"]
tpcds_tbl_col = {"dbgen_version": ["dv_version", "dv_create_date", "dv_create_time", "dv_cmdline_args"],
                 "warehouse": ["w_warehouse_sk", "w_warehouse_id", "w_warehouse_name", "w_warehouse_sq_ft",
                               "w_street_number", "w_street_name", "w_street_type", "w_suite_number", "w_city",
                               "w_county", "w_state", "w_zip", "w_country", "w_gmt_offset"],
                 "promotion": ["p_promo_sk", "p_promo_id", "p_start_date_sk", "p_end_date_sk", "p_item_sk", "p_cost",
                               "p_response_target", "p_promo_name", "p_channel_dmail", "p_channel_email",
                               "p_channel_catalog", "p_channel_tv", "p_channel_radio", "p_channel_press",
                               "p_channel_event", "p_channel_demo", "p_channel_details", "p_purpose",
                               "p_discount_active"],
                 "web_page": ["wp_web_page_sk", "wp_web_page_id", "wp_rec_start_date", "wp_rec_end_date",
                              "wp_creation_date_sk", "wp_access_date_sk", "wp_autogen_flag", "wp_customer_sk", "wp_url",
                              "wp_type", "wp_char_count", "wp_link_count", "wp_image_count", "wp_max_ad_count"],
                 "item": ["i_item_sk", "i_item_id", "i_rec_start_date", "i_rec_end_date", "i_item_desc",
                          "i_current_price", "i_wholesale_cost", "i_brand_id", "i_brand", "i_class_id", "i_class",
                          "i_category_id", "i_category", "i_manufact_id", "i_manufact", "i_size", "i_formulation",
                          "i_color", "i_units", "i_container", "i_manager_id", "i_product_name"],
                 "income_band": ["ib_income_band_sk", "ib_lower_bound", "ib_upper_bound"],
                 "time_dim": ["t_time_sk", "t_time_id", "t_time", "t_hour", "t_minute", "t_second", "t_am_pm",
                              "t_shift", "t_sub_shift", "t_meal_time"],
                 "catalog_page": ["cp_catalog_page_sk", "cp_catalog_page_id", "cp_start_date_sk", "cp_end_date_sk",
                                  "cp_department", "cp_catalog_number", "cp_catalog_page_number", "cp_description",
                                  "cp_type"],
                 "web_site": ["web_site_sk", "web_site_id", "web_rec_start_date", "web_rec_end_date", "web_name",
                              "web_open_date_sk", "web_close_date_sk", "web_class", "web_manager", "web_mkt_id",
                              "web_mkt_class", "web_mkt_desc", "web_market_manager", "web_company_id",
                              "web_company_name", "web_street_number", "web_street_name", "web_street_type",
                              "web_suite_number", "web_city", "web_county", "web_state", "web_zip", "web_country",
                              "web_gmt_offset", "web_tax_percentage"],
                 "ship_mode": ["sm_ship_mode_sk", "sm_ship_mode_id", "sm_type", "sm_code", "sm_carrier", "sm_contract"],
                 "customer_address": ["ca_address_sk", "ca_address_id", "ca_street_number", "ca_street_name",
                                      "ca_street_type", "ca_suite_number", "ca_city", "ca_county", "ca_state", "ca_zip",
                                      "ca_country", "ca_gmt_offset", "ca_location_type"],
                 "reason": ["r_reason_sk", "r_reason_id", "r_reason_desc"],
                 "store": ["s_store_sk", "s_store_id", "s_rec_start_date", "s_rec_end_date", "s_closed_date_sk",
                           "s_store_name", "s_number_employees", "s_floor_space", "s_hours", "s_manager", "s_market_id",
                           "s_geography_class", "s_market_desc", "s_market_manager", "s_division_id", "s_division_name",
                           "s_company_id", "s_company_name", "s_street_number", "s_street_name", "s_street_type",
                           "s_suite_number", "s_city", "s_county", "s_state", "s_zip", "s_country", "s_gmt_offset",
                           "s_tax_precentage"],
                 "customer_demographics": ["cd_demo_sk", "cd_gender", "cd_marital_status", "cd_education_status",
                                           "cd_purchase_estimate", "cd_credit_rating", "cd_dep_count",
                                           "cd_dep_employed_count", "cd_dep_college_count"],
                 "store_returns": ["sr_returned_date_sk", "sr_return_time_sk", "sr_item_sk", "sr_customer_sk",
                                   "sr_cdemo_sk", "sr_hdemo_sk", "sr_addr_sk", "sr_store_sk", "sr_reason_sk",
                                   "sr_ticket_number", "sr_return_quantity", "sr_return_amt", "sr_return_tax",
                                   "sr_return_amt_inc_tax", "sr_fee", "sr_return_ship_cost", "sr_refunded_cash",
                                   "sr_reversed_charge", "sr_store_credit", "sr_net_loss"],
                 "catalog_sales": ["cs_sold_date_sk", "cs_sold_time_sk", "cs_ship_date_sk", "cs_bill_customer_sk",
                                   "cs_bill_cdemo_sk", "cs_bill_hdemo_sk", "cs_bill_addr_sk", "cs_ship_customer_sk",
                                   "cs_ship_cdemo_sk", "cs_ship_hdemo_sk", "cs_ship_addr_sk", "cs_call_center_sk",
                                   "cs_catalog_page_sk", "cs_ship_mode_sk", "cs_warehouse_sk", "cs_item_sk",
                                   "cs_promo_sk", "cs_order_number", "cs_quantity", "cs_wholesale_cost",
                                   "cs_list_price", "cs_sales_price", "cs_ext_discount_amt", "cs_ext_sales_price",
                                   "cs_ext_wholesale_cost", "cs_ext_list_price", "cs_ext_tax", "cs_coupon_amt",
                                   "cs_ext_ship_cost", "cs_net_paid", "cs_net_paid_inc_tax", "cs_net_paid_inc_ship",
                                   "cs_net_paid_inc_ship_tax", "cs_net_profit"],
                 "inventory": ["inv_date_sk", "inv_item_sk", "inv_warehouse_sk", "inv_quantity_on_hand"],
                 "store_sales": ["ss_sold_date_sk", "ss_sold_time_sk", "ss_item_sk", "ss_customer_sk", "ss_cdemo_sk",
                                 "ss_hdemo_sk", "ss_addr_sk", "ss_store_sk", "ss_promo_sk", "ss_ticket_number",
                                 "ss_quantity", "ss_wholesale_cost", "ss_list_price", "ss_sales_price",
                                 "ss_ext_discount_amt", "ss_ext_sales_price", "ss_ext_wholesale_cost",
                                 "ss_ext_list_price", "ss_ext_tax", "ss_coupon_amt", "ss_net_paid",
                                 "ss_net_paid_inc_tax", "ss_net_profit"],
                 "web_returns": ["wr_returned_date_sk", "wr_returned_time_sk", "wr_item_sk", "wr_refunded_customer_sk",
                                 "wr_refunded_cdemo_sk", "wr_refunded_hdemo_sk", "wr_refunded_addr_sk",
                                 "wr_returning_customer_sk", "wr_returning_cdemo_sk", "wr_returning_hdemo_sk",
                                 "wr_returning_addr_sk", "wr_web_page_sk", "wr_reason_sk", "wr_order_number",
                                 "wr_return_quantity", "wr_return_amt", "wr_return_tax", "wr_return_amt_inc_tax",
                                 "wr_fee", "wr_return_ship_cost", "wr_refunded_cash", "wr_reversed_charge",
                                 "wr_account_credit", "wr_net_loss"],
                 "web_sales": ["ws_sold_date_sk", "ws_sold_time_sk", "ws_ship_date_sk", "ws_item_sk",
                               "ws_bill_customer_sk", "ws_bill_cdemo_sk", "ws_bill_hdemo_sk", "ws_bill_addr_sk",
                               "ws_ship_customer_sk", "ws_ship_cdemo_sk", "ws_ship_hdemo_sk", "ws_ship_addr_sk",
                               "ws_web_page_sk", "ws_web_site_sk", "ws_ship_mode_sk", "ws_warehouse_sk", "ws_promo_sk",
                               "ws_order_number", "ws_quantity", "ws_wholesale_cost", "ws_list_price", "ws_sales_price",
                               "ws_ext_discount_amt", "ws_ext_sales_price", "ws_ext_wholesale_cost",
                               "ws_ext_list_price", "ws_ext_tax", "ws_coupon_amt", "ws_ext_ship_cost", "ws_net_paid",
                               "ws_net_paid_inc_tax", "ws_net_paid_inc_ship", "ws_net_paid_inc_ship_tax",
                               "ws_net_profit"],
                 "customer": ["c_customer_sk", "c_customer_id", "c_current_cdemo_sk", "c_current_hdemo_sk",
                              "c_current_addr_sk", "c_first_shipto_date_sk", "c_first_sales_date_sk", "c_salutation",
                              "c_first_name", "c_last_name", "c_preferred_cust_flag", "c_birth_day", "c_birth_month",
                              "c_birth_year", "c_birth_country", "c_login", "c_email_address", "c_last_review_date_sk"],
                 "household_demographics": ["hd_demo_sk", "hd_income_band_sk", "hd_buy_potential", "hd_dep_count",
                                            "hd_vehicle_count"],
                 "catalog_returns": ["cr_returned_date_sk", "cr_returned_time_sk", "cr_item_sk",
                                     "cr_refunded_customer_sk", "cr_refunded_cdemo_sk", "cr_refunded_hdemo_sk",
                                     "cr_refunded_addr_sk", "cr_returning_customer_sk", "cr_returning_cdemo_sk",
                                     "cr_returning_hdemo_sk", "cr_returning_addr_sk", "cr_call_center_sk",
                                     "cr_catalog_page_sk", "cr_ship_mode_sk", "cr_warehouse_sk", "cr_reason_sk",
                                     "cr_order_number", "cr_return_quantity", "cr_return_amount", "cr_return_tax",
                                     "cr_return_amt_inc_tax", "cr_fee", "cr_return_ship_cost", "cr_refunded_cash",
                                     "cr_reversed_charge", "cr_store_credit", "cr_net_loss"],
                 "call_center": ["cc_call_center_sk", "cc_call_center_id", "cc_rec_start_date", "cc_rec_end_date",
                                 "cc_closed_date_sk", "cc_open_date_sk", "cc_name", "cc_class", "cc_employees",
                                 "cc_sq_ft", "cc_hours", "cc_manager", "cc_mkt_id", "cc_mkt_class", "cc_mkt_desc",
                                 "cc_market_manager", "cc_division", "cc_division_name", "cc_company",
                                 "cc_company_name", "cc_street_number", "cc_street_name", "cc_street_type",
                                 "cc_suite_number", "cc_city", "cc_county", "cc_state", "cc_zip", "cc_country",
                                 "cc_gmt_offset", "cc_tax_percentage"],
                 "date_dim": ["d_date_sk", "d_date_id", "d_date", "d_month_seq", "d_week_seq", "d_quarter_seq",
                              "d_year", "d_dow", "d_moy", "d_dom", "d_qoy", "d_fy_year", "d_fy_quarter_seq",
                              "d_fy_week_seq", "d_day_name", "d_quarter_name", "d_holiday", "d_weekend",
                              "d_following_holiday", "d_first_dom", "d_last_dom", "d_same_day_ly", "d_same_day_lq",
                              "d_current_day", "d_current_week", "d_current_month", "d_current_quarter",
                              "d_current_year"]}

# JOB schema
job_table_alias = {"aka_title": "at",
                   "char_name": "cn",
                   "role_type": "rt",
                   "comp_cast_type": "cct",
                   "movie_link": "ml",
                   "link_type": "lt",
                   "cast_info": "ci",
                   "complete_cast": "cc",
                   "title": "t",
                   "aka_name": "an",
                   "movie_companies": "mc",
                   "kind_type": "kt",
                   "name": "n",
                   "company_type": "ct",
                   "movie_keyword": "mk",
                   "movie_info": "mi",
                   "person_info": "pi",
                   "company_name": "cn",
                   "keyword": "k",
                   "movie_info_idx": "mi_idx",
                   "info_type": "it"}

# todo: cols selected!!!
tpch_tables = tpcds_tables
tpch_cols = tpcds_cols
tpch_tbl_col = tpcds_tbl_col

# victim model
heuristic = ["extend", "db2advis", "auto_admin", "drop", "relaxation", "anytime"]
rl_based = ["swirl", "drlinda", "dqn", "mcts",
            "swirl_statecol", "swirl_nomask",
            "drlinda_stateplan",
            "dqn_statecol",
            "dqn_norule2", "dqn_rule2",
            "dqn_norule3", "dqn_rule3"]

# reserved token
PAD = 0
UNK = 1
EOS = 2
BOS = 3
SEP = 4

WORD = {
    PAD: "<pad>",
    UNK: "<unk>",
    BOS: "<s>",
    EOS: "</s>",
    SEP: "<sep>"
}

# upper(): order_by_key, conjunction, join
# lower(): others

# dynamic
operator = ["=", "!=", ">", "<", "<=", ">=", "<>"]
operator_vocab = ["=", "!=", ">", "<", "<=", ">="]
aggregator = ["max", "min", "count", "avg", "sum"]
order_by_key = ["DESC", "ASC"]
conjunction = ["AND", "OR"]

# todo(0411): newly added.
# wildcard = ["*"]
wildcard = "*"
parenthesis = ["(", ")"]
null_operator = ["is"]

null_predicate = ["null", "not null"]
in_predicate = ["in", "not in"]
exists_predicate = ["exists", "not exists"]
like_predicate = ["like", "not like"]

# reserved
# todo(0411): newly added. "LEFT JOIN", "RIGHT JOIN", "INNER JOIN"
join = ["JOIN", "ON", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN"]
# punctuation = ["(", ")", ",", " ", ";"]
punctuation = [",", " ", ";"]

# todo: "aggregate"?
keyword = ["select", "from", "aggregate", "where", "group by", "having", "order by"]

# todo: to be classified.
# join = ["join", "cartesian", | "left join", "right join", "inner join"]
# predicate_type = ["between", "is null", "is not null", "in", "is not in", "exists", "not exists", "like", "not like"]

# node types
int_ops = ["Seq Scan", "Hash Join", "Nested Loop", "CTE Scan",
           "Index Only Scan", "Index Scan", "Merge Join", "Sort"]

ops = ["Aggregate", "BitmapAnd", "Hash Join", "Gather",
       "Nested Loop", "Gather Merge", "Materialize", "Bitmap Heap Scan",
       "Index Scan", "Merge Join", "Seq Scan", "Sort", "Hash",
       "Index Only Scan", "Bitmap Index Scan"]
