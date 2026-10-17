# -*- coding: utf-8 -*-
import io
ce = io.open('results/_w259bmc_derive_editor.py', encoding='utf-8', newline='').read()
i = ce.find('structural output gates')
print('canon W259 editor gates section:')
print(ce[i-50:i+3000])
