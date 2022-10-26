pval = c()
OR = c()

df = read.csv('linear_nona.csv', row.names = 'Patient_ID')
mpval = c()
mOR = c()

myf = 'Response ~ Feature_0+Feature_1+Feature_2+Feature_3+Feature_4+Feature_5+Feature_6+Feature_7+Feature_8'
mylogit2 <- stats::glm(myf, data = df, na.action=na.omit, family = 'binomial', maxit = 1000)
summary(mylogit2)
exp(cbind(OR = coef(mylogit2), confint(mylogit2, level=0.95)))

summary(mylogit2)$coefficients[,4]->mpval
exp(cbind(OR = coef(mylogit2), confint(mylogit2)))[,1]->mOR
write.csv(mpval, 'multi.pval.csv')
write.csv(mOR, 'multi.OR.csv')
