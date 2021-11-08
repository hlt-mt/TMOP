# TMop - Translation Memory Open-source Purifier


TMop is an open-source software written in Python designed for cleaning and maintaining a Translation Memory (*i.e.* a collection of ``(source, target)`` segments, called Translation Units, used to aid human translators operating in a Computer-assisted Translation framework). 

The goal of TMop is to identify and remove from the TM all the "bad" TUs,  in which any of the two textual elements is either: 

i) syntactically poor, 

ii) semantically different from the other,

iii) awkward according to some formatting criteria. 

TMop has been developed at [Fondazione Bruno Kessler](https://hlt-mt.fbk.eu) with the support of the European Association of Machine Translation (EAMT) and the European Project [Modern Machine Translation (MMT)](http://www.modernmt.eu). It can be downloaded as a package including: software, documentation, toy data and evaluation scripts. 

# Citing

If you use TMOP in your research, please cite [TMop: a Tool for Unsupervised Translation Memory Cleaning](https://aclanthology.org/P16-4009/).
```
@InProceedings{jalilisabet2016tmop,
  title = {TMop: a Tool for Unsupervised Translation Memory Cleaning},
  author = {Jalili Sabet, Masoud and Negri, Matteo and Turchi, Marco and de Souza, Jos{\'e} GC and Federico, Marcello},
  journal = {Proceedings of ACL-2016 System Demonstrations},
  pages = {49--54},
  year = {2016}
}
```

# Contacts

[Matteo Negri](http://hlt-mt.fbk.eu/people/profile/negri), Fondazione Bruno Kessler, Italy (negri_at_fbk.eu)

Masoud Jalili Sabet, Ludwig Maximilian University of Munich, Germany (jalili.masoud_at_cis.lmu.de)

[Marco Turchi](http://hlt-mt.fbk.eu/people/profile/turchi), Fondazione Bruno Kesler, Italy (turchi_at_fbk.eu)
