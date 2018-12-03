from multi_dirc import multi_dirc

a = multi_dirc('2018-01-01 00:00:00', '2018-01-02 00:00:00', 1000, [500, 1000, 1500, 2000, 2500])
print a.generate_all()
