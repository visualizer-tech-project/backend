# TON dataset inspection

## `counterparties/ton-v3-counterparties/counts.json`

- Size: 135 bytes
- Top-level type: `dict`
- Top-level keys: `['spend', 'reward']`
- Dict `spend` keys: `['transactions', 'actions']`
- Dict `reward` keys: `['transactions', 'actions']`

```json
{
  "spend": {
    "transactions": 17790,
    "actions": 17791
  },
  "reward": {
    "transactions": 50228,
    "actions": 26242
  }
}
```

## `counterparties/ton-v3-counterparties/reward_v3_actions.json`

- Size: 44155639 bytes
- Top-level type: `list`
- List length: **26242**
- First element type: `dict`
- First element keys: `['trace_id', 'action_id', 'start_lt', 'end_lt', 'start_utime', 'end_utime', 'trace_end_lt', 'trace_end_utime', 'trace_mc_seqno_end', 'transactions', 'success', 'type', 'details', 'trace_external_hash', 'trace_external_hash_norm', 'finality']`

```json
{
  "trace_id": "DQuM/UR2x/CoSTWhY/t75SFyQi7rtmfsGQ5HiTftpjM=",
  "action_id": "Q39C0Annt33SwzOzcrETLB0OuvvNJcC52X6VoFG088I=",
  "start_lt": "93307000000008",
  "end_lt": "93307000000009",
  "start_utime": 1785330571,
  "end_utime": 1785330571,
  "trace_end_lt": "93307000000009",
  "trace_end_utime": 1785330571,
  "trace_mc_seqno_end": 82744100,
  "transactions": [
    "DQuM/UR2x/CoSTWhY/t75SFyQi7rtmfsGQ5HiTftpjM=",
    "hvl6VoIc42KavTxZiEuH68rqGTPrlryE6RZG4wQENyk="
  ],
  "success": true,
  "type": "ton_transfer",
  "details": {
    "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
    "destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
    "value": "1000000000",
    "value_extra_currencies": {},
    "comment": null,
    "encrypted": false
  },
  "trace_external_hash": "0fudYu3TUW3oNEzgEUjJYOvheMNCBGlSJLR8JidolpY=",
  "trace_external_hash_norm": "EOv/kgNapTLNA4fHzK1ZcGWjqALNTPU6rAgADY2v5VE=",
  "finality": "finalized"
}
```

## `counterparties/ton-v3-counterparties/reward_v3_transactions.json`

- Size: 361232484 bytes
- Top-level type: `list`
- List length: **50228**
- First element type: `dict`
- First element keys: `['account', 'hash', 'lt', 'now', 'mc_block_seqno', 'trace_id', 'prev_trans_hash', 'prev_trans_lt', 'orig_status', 'end_status', 'total_fees', 'total_fees_extra_currencies', 'description', 'block_ref', 'in_msg', 'out_msgs', 'account_state_before', 'account_state_after', 'emulated', 'finality']`

```json
{
  "account": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
  "hash": "hvl6VoIc42KavTxZiEuH68rqGTPrlryE6RZG4wQENyk=",
  "lt": "93307000000009",
  "now": 1785330571,
  "mc_block_seqno": 82744100,
  "trace_id": "DQuM/UR2x/CoSTWhY/t75SFyQi7rtmfsGQ5HiTftpjM=",
  "prev_trans_hash": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
  "prev_trans_lt": "0",
  "orig_status": "nonexist",
  "end_status": "uninit",
  "total_fees": "0",
  "total_fees_extra_currencies": {},
  "description": {
    "type": "ord",
    "aborted": true,
    "destroyed": false,
    "credit_first": true,
    "storage_ph": {
      "storage_fees_collected": "0",
      "status_change": "unchanged"
    },
    "credit_ph": {
      "credit": "1000000000"
    },
    "compute_ph": {
      "skipped": true,
      "reason": "no_state"
    }
  },
  "block_ref": {
    "workchain": 0,
    "shard": "8000000000000000",
    "seqno": 87315937
  },
  "in_msg": {
    "hash": "JA+LIuKFc9zra5+7ZNtetb3USdTSkzmJhENnZH/LJZY=",
    "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
    "destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
    "value": "1000000000",
    "value_extra_currencies": {},
    "fwd_fee": "44446",
    "ihr_fee": "0",
    "extra_flags": "0",
    "created_lt": "93307000000008",
    "created_at": "1785330571",
    "opcode": null,
    "decoded_opcode": null,
    "ihr_disabled": true,
    "bounce": false,
    "bounced": false,
    "import_fee": null,
    "message_content": {
      "hash": "lqKW0iTyhcZ77pPDD4owkVfw2qNdxbh+QQt4YwoJz8c=",
      "body": "te6cckEBAQEAAgAAAEysuc0=",
      "decoded": {
        "@type": "empty_cell"
      }
    },
    "init_state": null
  },
  "out_msgs": [],
  "account_state_before": {
    "hash": "kK7Illr6uxbrw8ubQI665xthjXh4i8gNCYQ1k8rJjaQ=",
    "balance": null,
    "extra_currencies": null,
    "account_status": null,
    "frozen_hash": null,
    "data_hash": null,
    "code_hash": null
  },
  "account_state_after": {
    "hash": "rnbqO8koSqKRBs7pbAJvkEfh1B6d/FNC1YyvSZe1csw=",
    "balance": "1000000000",
    "extra_currencies": {},
    "account_status": "uninit",
    "frozen_hash": null,
    "data_hash": null,
    "code_hash": null
  },
  "emulated": false,
  "finality": "finalized"
}
```

## `counterparties/ton-v3-counterparties/spend_v3_actions.json`

- Size: 18262290 bytes
- Top-level type: `list`
- List length: **17791**
- First element type: `dict`
- First element keys: `['trace_id', 'action_id', 'start_lt', 'end_lt', 'start_utime', 'end_utime', 'trace_end_lt', 'trace_end_utime', 'trace_mc_seqno_end', 'transactions', 'success', 'type', 'details', 'trace_external_hash', 'trace_external_hash_norm', 'finality']`

```json
{
  "trace_id": "QX0ZLfu0U/VsEJFqnrCYj0UXq4JJJDNYL43rz7Umxa8=",
  "action_id": "MsaBop4gP9Atp+vND0ETosxQSwi+U7OzLVYhG1D8/PA=",
  "start_lt": "98304768000036",
  "end_lt": "98304768000037",
  "start_utime": 1787341205,
  "end_utime": 1787341205,
  "trace_end_lt": "98304768000037",
  "trace_end_utime": 1787341205,
  "trace_mc_seqno_end": 87623096,
  "transactions": [
    "0j6JAH5e7HNe74EgSXfuyRu3PQJWqg1y2HkPKP6wiCc=",
    "kHwEsFEhfyNc4R6w6aQBb8qps7NPFw5QGuYYkxhESkg="
  ],
  "success": true,
  "type": "ton_transfer",
  "details": {
    "source": "0:D887D0E2D1C4FC4126E71C970D33AB1896940000EAE703BB1AB6CECC830777E3",
    "destination": "0:7BF0875C8D19D1274207A4615E5BBAB9696AAB5D676C7478601A0EC558D4C460",
    "value": "1498700000",
    "value_extra_currencies": {},
    "comment": null,
    "encrypted": false
  },
  "trace_external_hash": "L1NKZDi+SSTHHf7i8VA+uNAn+qsljWxImUxQV3y1u/o=",
  "trace_external_hash_norm": "6NRdj7qGOrn4xSMwsR8vVNTB/xijopn6iZqTLjj7Qeg=",
  "finality": "finalized"
}
```

## `counterparties/ton-v3-counterparties/spend_v3_transactions.json`

- Size: 63677268 bytes
- Top-level type: `list`
- List length: **17790**
- First element type: `dict`
- First element keys: `['account', 'hash', 'lt', 'now', 'mc_block_seqno', 'trace_id', 'prev_trans_hash', 'prev_trans_lt', 'orig_status', 'end_status', 'total_fees', 'total_fees_extra_currencies', 'description', 'block_ref', 'in_msg', 'out_msgs', 'account_state_before', 'account_state_after', 'emulated', 'finality']`

```json
{
  "account": "0:7BF0875C8D19D1274207A4615E5BBAB9696AAB5D676C7478601A0EC558D4C460",
  "hash": "kHwEsFEhfyNc4R6w6aQBb8qps7NPFw5QGuYYkxhESkg=",
  "lt": "98304768000037",
  "now": 1787341205,
  "mc_block_seqno": 87623096,
  "trace_id": "QX0ZLfu0U/VsEJFqnrCYj0UXq4JJJDNYL43rz7Umxa8=",
  "prev_trans_hash": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
  "prev_trans_lt": "0",
  "orig_status": "nonexist",
  "end_status": "uninit",
  "total_fees": "0",
  "total_fees_extra_currencies": {},
  "description": {
    "type": "ord",
    "aborted": true,
    "destroyed": false,
    "credit_first": true,
    "storage_ph": {
      "storage_fees_collected": "0",
      "status_change": "unchanged"
    },
    "credit_ph": {
      "credit": "1498700000"
    },
    "compute_ph": {
      "skipped": true,
      "reason": "no_state"
    }
  },
  "block_ref": {
    "workchain": 0,
    "shard": "8000000000000000",
    "seqno": 92007602
  },
  "in_msg": {
    "hash": "0f6PIpTuIp0LL1p0bt7+xZQeX2FEvnNxOfJoRjLo770=",
    "source": "0:D887D0E2D1C4FC4126E71C970D33AB1896940000EAE703BB1AB6CECC830777E3",
    "destination": "0:7BF0875C8D19D1274207A4615E5BBAB9696AAB5D676C7478601A0EC558D4C460",
    "value": "1498700000",
    "value_extra_currencies": {},
    "fwd_fee": "44446",
    "ihr_fee": "0",
    "extra_flags": "0",
    "created_lt": "98304768000036",
    "created_at": "1787341205",
    "opcode": null,
    "decoded_opcode": null,
    "ihr_disabled": true,
    "bounce": false,
    "bounced": false,
    "import_fee": null,
    "message_content": {
      "hash": "lqKW0iTyhcZ77pPDD4owkVfw2qNdxbh+QQt4YwoJz8c=",
      "body": "te6cckEBAQEAAgAAAEysuc0=",
      "decoded": {
        "@type": "empty_cell"
      }
    },
    "init_state": null
  },
  "out_msgs": [],
  "account_state_before": {
    "hash": "kK7Illr6uxbrw8ubQI665xthjXh4i8gNCYQ1k8rJjaQ=",
    "balance": null,
    "extra_currencies": null,
    "account_status": null,
    "frozen_hash": null,
    "data_hash": null,
    "code_hash": null
  },
  "account_state_after": {
    "hash": "T9veYHBI416z2wC/cAPi168uXJUIUYMydJV0mQuY8IY=",
    "balance": "1498700000",
    "extra_currencies": {},
    "account_status": "uninit",
    "frozen_hash": null,
    "data_hash": null,
    "code_hash": null
  },
  "emulated": false,
  "finality": "finalized"
}
```

## `jettons/ton-v3-jettons/jetton_counts.json`

- Size: 35 bytes
- Top-level type: `dict`
- Top-level keys: `['spend', 'reward']`

```json
{
  "spend": 0,
  "reward": 25107
}
```

## `jettons/ton-v3-jettons/reward_v3_jetton_transfers.json`

- Size: 27604056 bytes
- Top-level type: `dict`
- Top-level keys: `['jetton_transfers', 'metadata', 'address_book']`
- List `jetton_transfers` length: **25107**
- First `jetton_transfers` element type: `dict`
- First `jetton_transfers` element keys: `['query_id', 'source', 'destination', 'amount', 'source_wallet', 'jetton_master', 'transaction_hash', 'transaction_lt', 'transaction_now', 'transaction_aborted', 'response_destination', 'custom_payload', 'decoded_custom_payload', 'forward_ton_amount', 'forward_payload', 'decoded_forward_payload', 'trace_id']`
- Dict `metadata` keys: `['0:0B4523C3A3BA59606082414C58EBAF79AFE15AF2144887BB10F341DCD7FC5042', '0:A175F54626DEE0D89040AF4B3DE22487569EF3D754548939F137C3A75A6546A0', '0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40', '0:533E09EEC7BC6B5BDE8D3D358D1133002264D930209054916C3353397D7ECF38', '0:11B84C232EA6BF8ECC678D5DDC0FADDEDD291B29B4F9789ED2788E2660A79E0C', '0:C3F3EFFBFF2E893EAAB350928444940D8CBBD800C1450ED26CA90E8E7C29CB6C', '0:26DA9A30CB75AB59EBB89B99DD36A423342BFED4C02B171E31397F65EE92A76D', '0:9004910D1713C7382BC4020E1F99712B0088AE0D554498FDDE9C6A8029805B25', '0:AC9B951A4955C48B045A613335C963BF559CCFF7C195D0EBDC470A66AEA06F95', '0:B113A994B5024A16719F69139328EB759596C38A25F59028B146FECDC3621DFE', '0:D90A8A89F0651BDCF819F6815A74CD53E301FF46D1BC3464985CA5F6981E46CF', '0:8592634708443F6D0D554F78F1062E64CCB99D89F91207E62FEC71395A364277']`
- Dict `address_book` keys: `['0:007579634B9FFC66BC4985B6BC69E46A8239AB878C5B768D1C8F5111568AC410', '0:00B3E9C9C638E28ED428B980910CA1D25A13F09B8E8DA3366FD4DE5393447686', '0:00C4B51D9411FA06B65ECD2EB2A88D0D863B03A700A45DB8034041B8BF4A2973', '0:00DBD59C6F24BB1A17974C0ABF66656E08B884AC57DC831E00FB191149347907', '0:0107AC17D5CEFA507F032111BEF150A48BDEFBE5C68CD42A68434F81E87983A7', '0:010C59DF750C46B2B61BF70F4415449CE6B2A615708D125B837C5CD09891BFAB', '0:017680D46E7C6B9E4588C63EBA7A06574E272597326D850E395B0FEB97B0899B', '0:01C7525B8FD8C10810B00FEB4D4D658A2710BE12E53A2BF7D0F1B7C140555A2F', '0:01CA33B45469A3BCB9CD496BFDF2532EDD27F0AA5C0B3A437A85E768C6C5220A', '0:01DA28F0149C40308740BF56A891CE224970607DEB99635B27668830A25A1BFE', '0:01DBB47A306E5F958B0F736811598590FC518056DAD523904D54A7EF37E3F666', '0:01F6E1237B54F7C2B2D7D853F3D9E59491714516D3CD0392407B5D7935B96A56', '0:0243EDAD8EDE3B675B5074F684653D46325B50164002C8C5E95A132E7ED2CBA6', '0:02482153146E19B2D47364C26A4F8CE02A1DAE23F1951A4EFAFE85CC4051AD3B', '0:02DE5D987DF3518626F183EAE9315F63C165BADA829F6AFC4902E6DA4198605F', '0:0490F242E2A1ED4D43E7E0A7893E83315B0052AA8062EEBACD1C0DF82BB07CA4', '0:04AD4B558186D445BE9743CAC13A820FA1490444EE022B0C30F864649262ADA5', '0:056EE52C11287FE5CDB76D56582B0E5AF78DB28FAE2D054CF98357DC447C91BC', '0:05712EB612E20B32B3A2AFD47D530FD0656B611D42696D7BA8E11F0945654BCD', '0:058F42AEC08CAC139B433894EE359923CCD43B489178B7C072053E525C16BEDC', '0:05CF12D1A78E5D479E6A02A72DDC8E8099B986E790D6E7A3E0CF69B6BDEE8CE1', '0:05FA86348D7C35D7AD29ACF039C02EFDCF110CECCA479DE0423FC24EC6227632', '0:062A43372AB5361003FCEF5BD2360270F4423058764521C668447E302B70E53A', '0:06BBC2CE9F4A081B34AAAC169308277533EB82D1993BF45696A8F2289ADDB75C', '0:06F6F3CC6168AEB62A3A78CCB0500DD83497F912B45CF9EAC8343DAA8975F862', '0:07355C1943B7363D2058A02F47F9FA0264D70E6561CC3EF67446779896B1DE3D', '0:073DE6A80122EEFA4768C4031F7B0AF9A1A6E6009BBE402E14008E5B6A8F57AD', '0:0745CC73C814C74B9C3262CF13EE4D8569F7C1BD3BC8CB759E90D50B44062C9D', '0:0755CB043FEC52107A11BBB8DB744D5BF926C71C0EC5C7B81A2AD578F82CAC0C', '0:07ACCF970AAEC3B0C5926B27F782C32A7827AE2B2C614AF55CDDD244EC0A27C6', '0:07CB77F96748692446A9D25D1D81A4C1093D75A0DED8F4D0BFF5652EF37A41C2', '0:07E189C12C1DCB8BC1C7E03EC588ECC1047885B8A14858362297E1C117E448C3', '0:07F69D45404434131C9C5BECDD97B5AB416458580510A1655DD155124E8C565E', '0:084BD0ED384AEA3BF96F60953F8C425470032B047063D82EA2DD1387B3694DAF', '0:0923AC4045D9CE9F9E53C5AFA41095235480703EBB67461BA25EE50E24585F44', '0:0960B5C56FDD5DB425EE371D8165D0CB3DFE8FE3732129113C138C753C05748D', '0:097F85C6D9104269EE3597A6D989B432ABFF51E822BF9B85E1632192CA243AC7', '0:09D35AC7FC33051747D8FCCFBDC84B56BF08BBFAF1B0FA8D3FAA06FDC43CF1A9', '0:0A7924FD57A7FB8362017A4C7458FD2C3259F4247561C9F03C12FA716A33C079', '0:0AF44716FAAD61363A2E9E469B1FA1AD79F64C12596D7423EDC42D2F07091541', '0:0B4523C3A3BA59606082414C58EBAF79AFE15AF2144887BB10F341DCD7FC5042', '0:0B4CDE31F3506F2D52E820F3A1E16BF2C114500DD515E853F349C7E6CD5F567C', '0:0B80221CCAA363A4F4A17ABEE72F2218181825C3FE7C6A5A66DBE43DBF166AB0', '0:0BA0D9EC44E25E5034291FC0308C825437B940E3054031EE0277D0B034C4022C', '0:0BAB036ABC712039AEFC6C65DE4764EDF42A9A62FCCDCF2D0C674B476A4C9ECA', '0:0C9AEDBFD9F893E3830510D4F834B81DFDD3C497187161DE71D33B5CA15E8BB7', '0:0CA547C6F347B71FB01F1F80C56A52715E1BE8D6E0DD609904353F40A397B81A', '0:0CB5190F1018EABE7E5BDA9D54917DD46F80E20EA620570A6FCBFB899BF207A3', '0:0CC6E6E5FF3ED1FBFA0C2222285A9E2C61CC26C1A999C7470818DD2CE2A144CE', '0:0D32D90D647541438D0854D795822330E9A72F1362A6E39CFA68C785FCD715BA']`

```json
{
  "jetton_transfers": [
    {
      "query_id": "6083770390912224534",
      "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "amount": "1000000000000",
      "source_wallet": "0:0B4523C3A3BA59606082414C58EBAF79AFE15AF2144887BB10F341DCD7FC5042",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "s6/eLba2wuwZOnoqTgtpMbOb7lT2gdotmpwmIbMSsq8=",
      "transaction_lt": "93307129000003",
      "transaction_now": 1785330624,
      "transaction_aborted": false,
      "response_destination": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "HtbPMwKll14sNQmZrudwwTmAP278pIdP5DDkEVHpZL4="
    },
    {
      "query_id": "6083770389269310771",
      "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "amount": "3000000000000",
      "source_wallet": "0:0B4523C3A3BA59606082414C58EBAF79AFE15AF2144887BB10F341DCD7FC5042",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "0Zle2/9q9jYBwQbz5FzCqg6S1ydYmEg2swzTs/tUdOc=",
      "transaction_lt": "93308830000025",
      "transaction_now": 1785331357,
      "transaction_aborted": false,
      "response_destination": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "iqWrrHpMFPjlQ2sOJ1AkHstp9Q4ecw5tLp4mkbVzHkk="
    },
    {
      "query_id": "4132614948697718259",
      "source": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "destination": "0:B201FFE50D736D2CFE9680B33BF95625B91842FA8148DF1F86849E5A1370E328",
      "amount": "67000000000",
      "source_wallet": "0:A175F54626DEE0D89040AF4B3DE22487569EF3D754548939F137C3A75A6546A0",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "cAfwPtuVjxFNirvIVn/rOFquVcwKQ8cx3ACUWiWbmxQ=",
      "transaction_lt": "93317810000003",
      "transaction_now": 1785335154,
      "transaction_aborted": false,
      "response_destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "DIOE9kIn16TxI5Cw9zJBbr06zttkhp7cTRTCC5I1nL0="
    },
    {
      "query_id": "2458570143630138311",
      "source": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "destination": "0:2508BB7AC06735EDE38A7C2BB6CED9E2BD2B2FA6172FF955BCC81D2482730D48",
      "amount": "67000000000",
      "source_wallet": "0:A175F54626DEE0D89040AF4B3DE22487569EF3D754548939F137C3A75A6546A0",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "zhkvjLgTZpeMS5zDam5JIIV0AK7UswaHeVbSN99w8q0=",
      "transaction_lt": "93318087000001",
      "transaction_now": 1785335277,
      "transaction_aborted": false,
      "response_destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "/XACUmGTR9yWqxboHM7effq1k7CxhFPthzhYgs1eC0k="
    },
    {
      "query_id": "15584593187463568910",
      "source": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "destination": "0:B201FFE50D736D2CFE9680B33BF95625B91842FA8148DF1F86849E5A1370E328",
      "amount": "67000000000",
      "source_wallet": "0:A175F54626DEE0D89040AF4B3DE22487569EF3D754548939F137C3A75A6546A0",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "Seh4hbNfoR9/O3BjbvPE9jWpsI5YG42XF5uYPtvLWJU=",
      "transaction_lt": "93320702000003",
      "transaction_now": 1785336398,
      "transaction_aborted": false,
      "response_destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "nvPxiXXgeyT2SiCKE3gD5VDhedK6rwQyDhTojaVlIMw="
    },
    {
      "query_id": "16034914103986558978",
      "source": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "destination": "0:0DCCD33F733B45F84F30650804058FD22E6EB29F88267EB9581F283D99D06A23",
      "amount": "67000000000",
      "source_wallet": "0:A175F54626DEE0D89040AF4B3DE22487569EF3D754548939F137C3A75A6546A0",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "L+CVjQJhbbB61K4RZ/4plAGIPSUxzXBJDSxadk64oHk=",
      "transaction_lt": "93320901000003",
      "transaction_now": 1785336481,
      "transaction_aborted": false,
      "response_destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "xXBVWWE7cJiIdg8JiWzzoVaY9pgeznwnUB7u7bYw/uw="
    },
    {
      "query_id": "6083770389528050636",
      "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "destination": "0:D8CA6DD04573304609A70EE5104A8D29090E1FC631B29A8E0411172AAA52885A",
      "amount": "10000000000000",
      "source_wallet": "0:0B4523C3A3BA59606082414C58EBAF79AFE15AF2144887BB10F341DCD7FC5042",
      "jetton_master": "0:D3061B39DA35C0F52ECFDF1B92BC2A21818A9B92541D2502D0F7C03736577B40",
      "transaction_hash": "CM6o6WeT6ZQhoqeDyKs9dZn7zfMSLyBqtHxdOLcp9n8=",
      "transaction_lt": "93325163000003",
      "transaction_now": 1785338274,
      "transaction_aborted": false,
      "response_destination": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "custom_payload": null,
      "decoded_custom_payload": null,
      "forward_ton_amount": "1",
      "forward_payload": null,
      "decoded_forward_payload": null,
      "trace_id": "Emsj0rjnZgdSm4E3+pvqK8l+YVL0bRxeZIfc4lrLHbs="
    },
    {
      "query_id": "6083770386999418440",
      "source": "0:21D6615A74625CA8BEB3C7A5777978A1239EE8148B1DF18C7B8A8A3215523DA0",
      "destination": 
...TRUNCATED...
```

## `jettons/ton-v3-jettons/spend_v3_jetton_transfers.json`

- Size: 68 bytes
- Top-level type: `dict`
- Top-level keys: `['jetton_transfers', 'metadata', 'address_book']`
- List `jetton_transfers` length: **0**
- Dict `metadata` keys: `[]`
- Dict `address_book` keys: `[]`

```json
{
  "jetton_transfers": [],
  "metadata": {},
  "address_book": {}
}
```
