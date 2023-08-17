
SELECT s_comment FROM part As p,partsupp As ps,supplier As s WHERE p.p_partkey = ps.ps_partkey AND s.s_suppkey = ps.ps_suppkey AND ps.ps_availqty = 6331 AND p.p_type > 'LARGE POLISHED NICKEL' AND p.p_retailprice < 1758.76 ORDER BY s_comment DESC;

SELECT s_comment FROM (SELECT * FROM part WHERE p_type > 'LARGE POLISHED NICKEL' AND p_retailprice < 1758.76 ) AS t408
INNER JOIN
(
    SELECT
        *
    FROM
        partsupp
    WHERE
        ps_availqty = 6331
) AS t409 ON t408.p_partkey = t409.ps_partkey
INNER JOIN
supplier as sp ON t409.ps_suppkey = sp.s_suppkey
ORDER BY s_comment DESC;
