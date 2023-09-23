from iptcinfo3 import IPTCInfo
import os
import exiv2

class ImageWriter:
    # A dictionary defining the maximum bytes for each IPTC tag.
    _max_bytes = {
        'Iptc.Application2.Byline'             :   32,
        'Iptc.Application2.BylineTitle'        :   32,
        'Iptc.Application2.Caption'            : 2000,
        'Iptc.Application2.City'               :   32,
        'Iptc.Application2.Contact'            :  128,
        'Iptc.Application2.Copyright'          :  128,
        'Iptc.Application2.CountryCode'        :    3,
        'Iptc.Application2.CountryName'        :   64,
        'Iptc.Application2.Credit'             :   32,
        'Iptc.Application2.Headline'           :  256,
        'Iptc.Application2.Keywords'           :   64,
        'Iptc.Application2.ObjectName'         :   64,
        'Iptc.Application2.Program'            :   32,
        'Iptc.Application2.ProgramVersion'     :   10,
        'Iptc.Application2.ProvinceState'      :   32,
        'Iptc.Application2.SpecialInstructions':  256,
        'Iptc.Application2.SubLocation'        :   32,
        'Iptc.Envelope.CharacterSet'           :   32,
        }


    def changeToRawExtension(self, file_path, newExtension):
        """
        Change the file extension to a specified one (generally to convert it to a RAW format).
        """
        base_path, extension = os.path.splitext(file_path)
        raw_file_path = base_path + "." + newExtension
        return raw_file_path
    
    @classmethod
    def truncate_iptc(cls, tag, value):
        """
        Truncate IPTC tag values based on their maximum allowed bytes.
        """
        if tag in cls._max_bytes:
            value = value.encode('utf-8')[:cls._max_bytes[tag]]
            value = value.decode('utf-8', errors='ignore')
        return value

    def set_iptc_value(self, iptcData, tag, value):
        """
        Set a value for a given IPTC tag in the provided IPTC data.
        """
        if not value:
            self.clear_iptc_tag(tag)
            return
        # make list of values
        key = exiv2.IptcKey(tag)
        type_id = exiv2.IptcDataSets.dataSetType(key.tag(), key.record())
        if type_id == exiv2.TypeId.date:
            values = [exiv2.DateValue(*value)]
        elif type_id == exiv2.TypeId.time:
            values = [exiv2.TimeValue(*value)]
        elif isinstance(value, (list, tuple)):
            values = [self.truncate_iptc(tag, x) for x in value]
        else:
            values = [self.truncate_iptc(tag, value)]
        # update or delete existing values
        datum = iptcData.findKey(key)
        while datum != iptcData.end():
            if datum.key() == tag:
                if values:
                    datum.setValue(values.pop(0))
                else:
                    datum = iptcData.erase(datum)
                    continue
            next(datum)
        # append remaining values
        while values:
            datum = exiv2.Iptcdatum(key)
            datum.setValue(values.pop(0))
            if iptcData.add(datum) != 0:
                print('duplicated tag %s', tag)
                return
        return iptcData
    
    def writeTagsFromPredictionsInImages(self, predictions, applyToRaw, overwrite):
        """
        Write tags (predicted keywords) into the images' IPTC metadata.

        Args:
        - predictions: A list of predicted objects containing image paths and their associated keywords.
        - applyToRaw: A boolean indicating whether to apply changes to RAW format images.
        - overwrite: A boolean indicating whether to overwrite existing keywords in the IPTC data.
        """
        startApplyToRaw = applyToRaw
        for prediction in predictions:
            applyToRaw = startApplyToRaw
            filename = prediction.path
            filenameRaw = None

            iptcInfo = IPTCInfo(filename, force=True)
            iptcInfoRaw = None
            if applyToRaw:
                extensions = ['dng','DNG']
                for extension in extensions:
                    filenameRaw = self.changeToRawExtension(filename, extension)
                    if os.path.exists(filenameRaw):
                        iptcInfoRaw = exiv2.ImageFactory.open(filenameRaw)
                        iptcInfoRaw.readMetadata()
                        break
                applyToRaw = iptcInfoRaw != None                
            
            addedKeywords = []

            if overwrite:
                iptcInfo['keywords'] = []

            for keyword in prediction.keywords:
                if keyword not in iptcInfo['keywords']:
                    iptcInfo['keywords'].append(keyword)
                    addedKeywords.append(keyword)     

            try:
                iptcInfo.save()
                tempFilename = filename + "~"
                if os.path.exists(tempFilename):
                    os.remove(tempFilename)
            except Exception as e:
                print('Error in file "'+filename+'" : \n\t', e)

            if applyToRaw:
                try:
                    iptcData = iptcInfoRaw.iptcData()
                    iptcData = self.set_iptc_value(iptcData, 'Iptc.Envelope.CharacterSet', '\x1b%G')
                    iptcData = self.set_iptc_value(iptcData,"Iptc.Application2.Keywords",addedKeywords)
                    iptcInfoRaw.setIptcData(iptcData)
                    iptcInfoRaw.writeMetadata()
                except Exception as e:
                    print('Error in file "'+filenameRaw+'" : \n\t', e)     

            