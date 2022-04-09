select
			substring(c_phone from 1 for 2) as cntrycode,
			c_acctbal
		from
			customer
		where
			not exists (
				select
					*
				from
					orders
				where
					o_custkey = c_custkey
			)