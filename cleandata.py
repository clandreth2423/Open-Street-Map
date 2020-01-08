#!/usr/bin/env python
# coding: utf-8

import xml.etree.cElementTree as ET


def update_street(element):
    """
    Updates the street type based on mapping of a tag 
    element whose key is 'addr:street'.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    This function makes the street types consistent:
        St. -> Street
        Rd -> Road
        ...
    """
    
    # Valid street suffixes and abbreviation mappings sourced from:
    # USPS - C1 Street Suffix Abbreviations
    # https://pe.usps.com/text/pub28/28apc_002.htm
    
    USPS_expected = [
        "Alley", "Anex", "Arcade", "Avenue", "Bayou", "Beach", "Bend", "Bluff", "Bluffs", "Bottom", "Boulevard", "Branch", 
        "Bridge", "Brook", "Brooks", "Burg", "Burgs", "Bypass", "Camp", "Canyon", "Cape", "Causeway", "Center", "Centers", 
        "Circle", "Cliff", "Cliffs", "Club", "Common", "Commons", "Corner", "Corners", "Course", "Court", "Courts", 
        "Cove", "Coves", "Creek", "Crescent", "Crest", "Crossing", "Crossroad", "Crossroads", "Curve", "Dale", "Dam", 
        "Divide", "Drive", "Drives", "Estate", "Estates", "Expressway", "Extension", "Extensions", "Falls", "Ferry", 
        "Field", "Fields", "Flat", "Flats", "Ford", "Fords", "Forest", "Forge", "Forges", "Fork", "Forks", "Fort", 
        "Freeway", "Garden", "Gateway", "Glen", "Glens", "Green", "Greens", "Grove", "Groves", "Harbor", "Harbors", "Haven", 
        "Heights", "Highway", "Hill", "Hills", "Hollow", "Inlet", "Island", "Islands", "Isle", "Junction", "Junctions", 
        "Key", "Keys", "Knoll", "Knolls", "Lake", "Lakes", "Landing", "Lane", "Light", "Lights", "Loaf", "Lock", "Locks", 
        "Lodge", "Loop", "Manor", "Manors", "Meadows", "Mill", "Mills", "Mission", "Motorway", "Mount", "Mountain", 
        "Mountains", "Neck", "Orchard", "Oval", "Overpass", "Park", "Parks", "Parkway", "Parkways", "Passage", "Path", 
        "Pike", "Pine", "Pines", "Place", "Plain", "Plains", "Plaza", "Point", "Points", "Port", "Ports", "Prairie", 
        "Radial", "Ranch", "Rapid", "Rapids", "Rest", "Ridge", "Ridges", "River", "Road", "Roads", "Route", "Shoal", "Shoals", 
        "Shore", "Shores", "Skyway", "Spring", "Square", "Squares", "Station", "Stravenue", "Stream", "Street", "Streets", 
        "Summit", "Terrace", "Throughway", "Trace", "Track", "Trafficway", "Trail", "Trailer", "Tunnel", "Turnpike", 
        "Underpass", "Union", "Unions", "Valley", "Valleys", "Viaduct", "View", "Views", "Village", "Villages", "Ville", 
        "Vista", "Way", "Well", "Wells"
    ]
    
    # These additional expected street suffixes are assumed 
    # to be acceptable for data cleaning purposes
    
    addl_expected = [
        "Arsenal", "Cary", "Chase", "Cloisters", "Close", "Conn", "Concourse", 
        "Driveway", "Farm", "Greene", "James", "Level", "Mews", "Needle", 
        "Oaks", "Overlook", "Pass", "Pathway", "Ramon", "Row", "Run", 
        "Sage", "Slip", "Trek", "Turn", "Walk", "Waye"
    ]
    
    mapping = {
        "Allee": "Alley", "Ally": "Alley", "Aly": "Alley", "Allee.": "Alley", "Ally.": "Alley", "Aly.": "Alley", 
        "Annex": "Anex", "Annx": "Anex", "Anx": "Anex", "Annex.": "Anex", "Annx.": "Anex", "Anx.": "Anex", 
        "Arc": "Arcade", "Arc.": "Arcade", 
        "Av": "Avenue", "Ave": "Avenue", "Aven": "Avenue", "Avenu": "Avenue", "Avn": "Avenue", "Avnue": "Avenue", 
        "Av.": "Avenue", "Ave.": "Avenue", "Aven.": "Avenue", "Avenu.": "Avenue", "Avn.": "Avenue", "Avnue.": "Avenue", 
        "Bayoo": "Bayou", "Byu": "Bayou", "Bayoo.": "Bayou", "Byu.": "Bayou", 
        "Bch": "Beach", "Bch.": "Beach", 
        "Bnd": "Bend", "Bnd.": "Bend", 
        "Blf": "Bluff", "Bluf": "Bluff", "Blfs": "Bluffs", "Blfs.": "Bluffs", 
        "Bot": "Bottom", "Btm": "Bottom", "Bottm": "Bottom", "Bot.": "Bottom", "Btm.": "Bottom", "Bottm.": "Bottom", 
        "Blvd": "Boulevard", "Boul": "Boulevard", "Boulv": "Boulevard", 
        "Blvd.": "Boulevard", "Boul.": "Boulevard", "Boulv.": "Boulevard", 
        "Br": "Branch", "Brnch": "Branch", "Br.": "Branch", "Brnch.": "Branch", 
        "Brdge": "Bridge", "Brg": "Bridge", "Brdge.": "Bridge", "Brg.": "Bridge", 
        "Brk": "Brook", "Brk.": "Brook", "Brks": "Brooks", "Brks.": "Brooks", 
        "Bg": "Burg", "Bg.": "Burg", "Bgs": "Burgs", "Bgs.": "Burgs", 
        "Byp": "Bypass", "Bypa": "Bypass", "Bypas": "Bypass", "Byps": "Bypass", 
        "Byp.": "Bypass", "Bypa.": "Bypass", "Bypas.": "Bypass", "Byps.": "Bypass", 
        "Cp": "Camp", "Cmp": "Camp", "Cp.": "Camp", "Cmp.": "Camp", 
        "Canyn": "Canyon", "Cnyn": "Canyon", "Cyn": "Canyon", "Canyn.": "Canyon", "Cnyn.": "Canyon", "Cyn.": "Canyon", 
        "Cpe": "Cape", "Cpe.": "Cape", 
        "Causwa": "Causeway", "Cswy": "Causeway", 
        "Cen": "Center", "Cent": "Center", "Centr": "Center", "Centre": "Center", 
        "Cnter": "Center", "Cntr": "Center", "Ctr": "Center", 
        "Cen.": "Center", "Cent.": "Center", "Centr.": "Center", "Centre.": "Center", 
        "Cnter.": "Center", "Cntr.": "Center", "Ctr.": "Center", "Ctrs": "Centers", "Ctrs.": "Centers", 
        "Cir": "Circle", "Circ": "Circle", "Circl": "Circle", "Crcl": "Circle", "Crcle": "Circle", 
        "Cir.": "Circle", "Circ.": "Circle", "Circl.": "Circle", "Crcl.": "Circle", "Crcle.": "Circle", 
        "Cirs": "Circle", "Cirs.": "Circle", 
        "Clf": "Cliff", "Clf.": "Cliff", "Clfs": "Cliffs", "Clfs.": "Cliffs", 
        "Clb": "Club", "Clb.": "Club", 
        "Cmn": "Common", "Cmn.": "Common", "Cmns": "Commons", "Cmns.": "Commons", 
        "Cor": "Corner", "Cor.": "Corner", "Cors": "Corners", "Cors.": "Corners", 
        "Crse": "Course", "Crse.": "Course", 
        "Ct": "Court", "Ct.": "Court", "Cts": "Courts", "Cts.": "Courts", 
        "Cv": "Cove", "Cv.": "Cove", "Cvs": "Coves", "Cvs.": "Coves", 
        "Crk": "Creek", "Crk.": "Creek", 
        "Cres": "Crescent", "Crsent": "Crescent", "Crsnt": "Crescent", 
        "Cres.": "Crescent", "Crsent.": "Crescent", "Crsnt.": "Crescent", 
        "Crst": "Crest", "Crst.": "Crest", 
        "Crssng": "Crossing", "Xing": "Crossing", "Crssng.": "Crossing", "Xing.": "Crossing", 
        "Xrd": "Crossroad", "Xrd.": "Crossroad", "Xrds": "Crossroads", "Xrds.": "Crossroads", 
        "Curv": "Curve", "Curv.": "Curve", 
        "Dl": "Dale", "Dl.": "Dale", 
        "Dm": "Dam", "Dm.": "Dam", 
        "Div": "Divide", "Dv": "Divide", "Dvd": "Divide", "Div.": "Divide", "Dv.": "Divide", "Dvd.": "Divide", 
        "Dr": "Drive", "Driv": "Drive", "Drv": "Drive", "Dr.": "Drive", "Driv.": "Drive", "Drv.": "Drive", 
        "Drs": "Drives", "Drs.": "Drives", 
        "Est": "Estate", "Est.": "Estate", "Ests": "Estates", "Ests.": "Estates", 
        "Exp": "Expressway", "Expr": "Expressway", "Express": "Expressway", "Expw": "Expressway", "Expy": "Expressway", 
        "Exp.": "Expressway", "Expr.": "Expressway", "Express.": "Expressway", "Expw.": "Expressway", "Expy.": "Expressway", 
        "Ext": "Extension", "Extn": "Extension", "Extnsn": "Extension", 
        "Ext.": "Extension", "Extn.": "Extension", "Extnsn.": "Extension", 
        "Exts": "Extensions", "Exts.": "Extensions", 
        "Fls": "Falls", "Fls.": "Falls", 
        "Fry": "Ferry", "Frry": "Ferry", "Fry.": "Ferry", "Frry.": "Ferry", 
        "Fld": "Field", "Fld.": "Field", "Flds": "Fields", "Flds.": "Fields", 
        "Flt": "Flat", "Flt.": "Flat", "Flts": "Flats", "Flts.": "Flats", 
        "Frd": "Ford", "Frd.": "Ford", "Frds": "Fords", "Frds.": "Fords", 
        "Forests": "Forest", "Frst": "Forest", "Forests.": "Forest", "Frst.": "Forest", 
        "Forg": "Forge", "Frg": "Forge", "Forg.": "Forge", "Frg.": "Forge", "Frgs": "Forges", "Frgs.": "Forges", 
        "Frk": "Fork", "Frk.": "Fork", "Frks.": "Forks", "Frks.": "Forks", 
        "Frt": "Fort", "Ft": "Fort", "Frt.": "Fort", "Ft.": "Fort", 
        "Freewy": "Freeway", "Frway": "Freeway", "Frwy": "Freeway", "Fwy": "Freeway", 
        "Freewy.": "Freeway", "Frway.": "Freeway", "Frwy.": "Freeway", "Fwy.": "Freeway", 
        "Gardn": "Garden", "Grden": "Garden", "Grdn": "Garden", "Gdn": "Garden", 
        "Gardn.": "Garden", "Grden.": "Garden", "Grdn.": "Garden", "Gdn.": "Garden", 
        "Gdns": "Garden", "Grdns": "Garden", "Gdns.": "Garden", "Grdns.": "Garden", 
        "Gatewy": "Gateway", "Gatway": "Gateway", "Gtway": "Gateway", "Gtwy": "Gateway", 
        "Gatewy.": "Gateway", "Gatway.": "Gateway", "Gtway.": "Gateway", "Gtwy.": "Gateway", 
        "Gln": "Glen", "Gln.": "Glen", "Glns": "Glens", "Glns.": "Glens", 
        "Grn": "Green", "Grn.": "Green", "Grns": "Greens", "Grns.": "Greens", 
        "Grov": "Grove", "Grv": "Grove", "Grov.": "Grove", "Grv.": "Grove", "Grvs": "Groves", "Grvs.": "Groves", 
        "Harb": "Harbor", "Harbr": "Harbor", "Hbr": "Harbor", "Hrbor": "Harbor", 
        "Harb.": "Harbor", "Harbr.": "Harbor", "Hbr.": "Harbor", "Hrbor.": "Harbor", "Hbrs": "Harbors", "Hbrs.": "Harbors", 
        "Hvn": "Haven", "Hvn.": "Haven", 
        "Ht": "Heights", "Hts": "Heights", "Ht.": "Heights", "Hts.": "Heights", 
        "Highwy": "Highway", "Hiway": "Highway", "Hiwy": "Highway", "Hway": "Highway", "Hwy": "Highway", 
        "Highwy.": "Highway", "Hiway.": "Highway", "Hiwy.": "Highway", "Hway.": "Highway", "Hwy.": "Highway", 
        "Hl": "Hill", "Hl.": "Hill", "Hls": "Hills", "Hls.": "Hills", 
        "Hllw": "Hollow", "Hollows": "Hollow", "Holw": "Hollow", "Holws": "Hollow", 
        "Hllw.": "Hollow", "Hollows.": "Hollow", "Holw.": "Hollow", "Holws.": "Hollow", 
        "Inlt": "Inlet", "Inlt.": "Inlet", 
        "Is": "Island", "Islnd": "Island", "Is.": "Island", "Islnd.": "Island", 
        "Iss": "Islands", "Islnds": "Islands", "Iss.": "Islands", "Islnds.": "Islands", 
        "Isles": "Isle", "Isles.": "Isle", 
        "Jct": "Junction", "Jction": "Junction", "Jctn": "Junction", "Junctn": "Junction", "Juncton": "Junction", 
        "Jct.": "Junction", "Jction.": "Junction", "Jctn.": "Junction", "Junctn.": "Junction", "Juncton.": "Junction", 
        "Jctns": "Junctions", "Jcts": "Junctions", "Jctns.": "Junctions", "Jcts.": "Junctions", 
        "Ky": "Key", "Ky.": "Key", "Kys": "Keys", "Kys.": "Keys", 
        "Knl": "Knoll", "Knol": "Knoll", "Knl.": "Knoll", "Knol.": "Knoll", "Knls": "Knolls", "Knls.": "Knolls", 
        "Lk": "Lake", "Lk.": "Lake", "Lks": "Lakes", "Lks.": "Lakes", 
        "Lndg": "Landing", "Lndng": "Landing", "Lndg.": "Landing", "Lndng.": "Landing", 
        "Ln": "Lane", "Ln.": "Lane", 
        "Lgt": "Light", "Lgt.": "Light", "Lgts": "Lights", "Lgts.": "Lights", 
        "Lf": "Loaf", "Lf.": "Loaf", 
        "Lck": "Lock", "Lck.": "Lock", "Lcks": "Locks", "Lcks.": "Locks", 
        "Ldg": "Lodge", "Ldge": "Lodge", "Lodg": "Lodge", "Ldg.": "Lodge", "Ldge.": "Lodge", "Lodg.": "Lodge", 
        "Loops": "Loop", "Loops.": "Loop", 
        "Mnr": "Manor", "Mnr.": "Manor", "Mnrs": "Manors", "Mnrs.": "Manors", 
        "Mdw": "Meadows", "Mdws": "Meadows", "Medows": "Meadows", "Mdw.": "Meadows", "Mdws.": "Meadows", "Medows.": "Meadows", 
        "Ml": "Mill", "Ml.": "Mill", "Mls": "Mills", "Mls.": "Mills", 
        "Missn": "Mission", "Mssn": "Mission", "Msn": "Mission", "Missn.": "Mission", "Mssn.": "Mission", "Msn.": "Mission", 
        "Mtwy": "Motorway", "Mtwy.": "Motorway", 
        "Mnt": "Mount", "Mt": "Mount", "Mnt.": "Mount", "Mt.": "Mount", 
        "Mntain": "Mountain", "Mntn": "Mountain", "Mountin": "Mountain", "Mtin": "Mountain", "Mtn": "Mountain", 
        "Mntain.": "Mountain", "Mntn.": "Mountain", "Mountin.": "Mountain", "Mtin.": "Mountain", "Mtn.": "Mountain", 
        "Mntns": "Mountains", "Mtns": "Mountains", "Mntns.": "Mountains", "Mtns.": "Mountains", 
        "Nck": "Neck", "Nck.": "Neck", 
        "Orch": "Orchard", "Orchrd": "Orchard", "Orch.": "Orchard", "Orchrd.": "Orchard", 
        "Ovl": "Oval", "Ovl.": "Oval", 
        "Opas": "Overpass", "Opas.": "Overpass", 
        "Prk": "Park", "Prk.": "Park", "Prks": "Parks", "Prks.": "Parks", 
        "Parkwy": "Parkway", "Pkway": "Parkway", "Pkwy": "Parkway", "Pky": "Parkway", 
        "Parkwy.": "Parkway", "Pkway.": "Parkway", "Pkwy.": "Parkway", "Pky.": "Parkway", 
        "Pkwys": "Parkways", "Pkwys.": "Parkways", 
        "Psge": "Passage", "Psge.": "Passage", 
        "Paths": "Path", "Paths.": "Path", 
        "Pikes": "Pike", "Pikes.": "Pike", 
        "Pne": "Pine", "Pne.": "Pine", "Pnes": "Pines", "Pnes.": "Pines", 
        "Pl": "Place", "Pl.": "Place", 
        "Pln": "Plain", "Pln.": "Plain", "Plns": "Plains", "Plns.": "Plains", 
        "Plz": "Plaza", "Plza": "Plaza", "Plz.": "Plaza", "Plza.": "Plaza", 
        "Pt": "Point", "Pt.": "Point", "Pts": "Points", "Pts.": "Points", 
        "Prt": "Port", "Prt.": "Port", "Prts": "Ports", "Prts.": "Ports", 
        "Pr": "Prairie", "Prr": "Prairie", "Pr.": "Prairie", "Prr.": "Prairie", 
        "Rad": "Radial", "Radiel": "Radial", "Radl": "Radial", "Rad.": "Radial", "Radiel.": "Radial", "Radl.": "Radial", 
        "Ranches": "Ranch", "Rnch": "Ranch", "Rnchs": "Ranch", "Ranches.": "Ranch", "Rnch.": "Ranch", "Rnchs.": "Ranch", 
        "Rpd": "Rapid", "Rpd.": "Rapid", "Rpds": "Rapids", "Rpds.": "Rapids", 
        "Rst": "Rest", "Rst.": "Rest", 
        "Rdg": "Ridge", "Rdge": "Ridge", "Rdg.": "Ridge", "Rdge.": "Ridge", 
        "Rdgs": "Ridges", "Rdges": "Ridges", "Rdgs.": "Ridge", "Rdges.": "Ridges", 
        "Riv": "River", "Rvr": "River", "Rivr": "River", "Riv.": "River", "Rvr.": "River", "Rivr.": "River", 
        "Rd": "Road", "Rd.": "Road", "Rds": "Roads", "Rds.": "Roads", 
        "Rte": "Route", "Rte.": "Route", 
        "Shl": "Shoal", "Shl.": "Shoal", "Shls": "Shoals", "Shls.": "Shoals", 
        "Shoar": "Shore", "Shr": "Shore", "Shoar.": "Shore", "Shr.": "Shore", 
        "Shoars": "Shores", "Shrs": "Shores", "Shoars.": "Shores", "Shrs.": "Shores", 
        "Skwy": "Skyway", "Skwy.": "Skyway", 
        "Spg": "Spring", "Spng": "Spring", "Sprng": "Spring", "Spg.": "Spring", "Spng.": "Spring", "Sprng.": "Spring", 
        "Spgs": "Spring", "Spngs": "Spring", "Sprngs": "Spring", "Spgs.": "Spring", "Spngs.": "Spring", "Sprngs.": "Spring", 
        "Sq": "Square", "Sqr": "Square", "Sqre": "Square", "Squ": "Square", 
        "Sq.": "Square", "Sqr.": "Square", "Sqre.": "Square", "Squ.": "Square", 
        "Sqs": "Squares", "Sqrs": "Squares", "Sqs.": "Squares", "Sqrs.": "Squares", 
        "Sta": "Station", "Statn": "Station", "Stn": "Station", "Sta.": "Station", "Statn.": "Station", "Stn.": "Station", 
        "Stra": "Stravenue", "Strav": "Stravenue", "Straven": "Stravenue", 
        "Stravn": "Stravenue", "Strvn": "Stravenue", "Strvnue": "Stravenue", 
        "Stra.": "Stravenue", "Strav.": "Stravenue", "Straven.": "Stravenue", 
        "Stravn.": "Stravenue", "Strvn.": "Stravenue", "Strvnue.": "Stravenue", 
        "Streme": "Stream", "Strm": "Stream", "Streme.": "Stream", "Strm.": "Stream", 
        "St": "Street", "Strt": "Street", "Str": "Street", "St.": "Street", "Strt.": "Street", "Str.": "Street", 
        "Sts": "Streets", "Sts.": "Streets", 
        "Smt": "Summit", "Sumit": "Summit", "Sumitt": "Summit", "Smt.": "Summit", "Sumit.": "Summit", "Sumitt.": "Summit", 
        "Ter": "Terrace", "Terr": "Terrace", "Ter.": "Terrace", "Terr.": "Terrace", 
        "Trwy": "Throughway", "Trwy.": "Throughway", 
        "Trce": "Trace", "Traces": "Trace", "Trce.": "Trace", "Traces.": "Trace", 
        "Tracks": "Track", "Trak": "Track", "Trk": "Track", "Trks": "Track", 
        "Tracks.": "Track", "Trak.": "Track", "Trk.": "Track", "Trks.": "Track", 
        "Trfy": "Trafficway", "Trfy.": "Trafficway", 
        "Trails": "Trail", "Trl": "Trail", "Trls": "Trail", "Trails.": "Trail", "Trl.": "Trail", "Trls.": "Trail", 
        "Trlr": "Trailer", "Trlrs": "Trailer", "Trlr.": "Trailer", "Trlrs.": "Trailer", 
        "Tunel": "Tunnel", "Tunl": "Tunnel", "Tunls": "Tunnel", "Tunnels": "Tunnel", "Tunnl": "Tunnel", 
        "Tunel.": "Tunnel", "Tunl.": "Tunnel", "Tunls.": "Tunnel", "Tunnels.": "Tunnel", "Tunnl.": "Tunnel", 
        "Trnpk": "Turnpike", "Turnpk": "Turnpike", "Tpke": "Turnpike", 
        "Trnpk.": "Turnpike", "Turnpk.": "Turnpike", "Tpke.": "Turnpike", 
        "Upas": "Underpass", "Upas.": "Underpass", 
        "Un": "Union", "Un.": "Union", "Uns": "Unions", "Uns.": "Unions", 
        "Vally": "Valley", "Vlly": "Valley", "Vly": "Valley", "Vally.": "Valley", "Vlly.": "Valley", "Vly.": "Valley", 
        "Vallys": "Valleys", "Vllys": "Valleys", "Vlys": "Valleys", 
        "Vallys.": "Valleys", "Vllys.": "Valleys", "Vlys.": "Valleys", 
        "Vdct": "Viaduct", "Via": "Viaduct", "Viadct": "Viaduct", "Vdct.": "Viaduct", "Via.": "Viaduct", "Viadct.": "Viaduct", 
        "Vw": "View", "Vw.": "View", "Vws": "Views", "Vws.": "Views", 
        "Vill": "Village", "Villag": "Village", "Villg": "Village", "Villiage": "Village", "Vlg": "Village", 
        "Vill.": "Village", "Villag.": "Village", "Villg.": "Village", "Villiage.": "Village", "Vlg.": "Village", 
        "Vills": "Villages", "Villags": "Villages", "Villgs": "Villages", "Villiages": "Villages", "Vlgs": "Villages", 
        "Vills.": "Villages", "Villags.": "Villages", "Villgs.": "Villages", "Villiages.": "Villages", "Vlgs.": "Villages", 
        "Vl": "Ville", "Vl.": "Ville", 
        "Vis": "Vista", "Vist": "Vista", "Vst": "Vista", "Vsta": "Vista", 
        "Vis.": "Vista", "Vist.": "Vista", "Vst.": "Vista", "Vsta.": "Vista", 
        "Wy": "Way", "Wy.": "Way", 
        "Wl": "Well", "Wl.": "Well", "Wls": "Wells", "Wls.": "Wells"
    }
    
    # While mapping can be applied to any US address 
    # from the OpenStreetMap database, addl_mapping 
    # applies specifically to certain data cleaning 
    # purposes within this dataset
    
    addl_mapping = {
        "I-95" : "Interstate 95", "Roademergency=yes" : "Road"
    }
    
    # The direction suffix allows the cleaning to look at the 
    # second to the last string in the addr:street value 
    # for any unexpected street types to clean
    
    direction_suffix = [
        "N", "N.", "N*", "North", 
        "S", "S.", "S*", "South", 
        "E", "E.", "E*", "East", 
        "W", "W.", "W*", "West"
    ]
    
    def update_street_type(street_name):
        words = street_name.split(' ')
        
        if words[-1] in direction_suffix:
            if words[-2] not in [*USPS_expected, *addl_expected]:
                if words[-2] in mapping.keys():
                    words[-2] = mapping[words[-2]]
                elif words[-2] in addl_mapping.keys():
                    words[-2] = addl_mapping[words[-2]]
        else:
            if words[-1] not in [*USPS_expected, *addl_expected]:
                if words[-1] in mapping.keys():
                    words[-1] = mapping[words[-1]]
                elif words[-1] in addl_mapping.keys():
                    words[-1] = addl_mapping[words[-1]]
                    
        words = " ".join(words)
        
        return words
    
    def is_street_name(elem):
        return (elem.attrib['k'] == "addr:street")
    
    for tag in element.iter("tag"):
        if is_street_name(tag):
            tag.attrib['v'] = update_street_type(tag.attrib['v'])
    
    return element


def update_street_direction(element):
    """
    Updates the abbreviations of street directions 
    based on mapping of a tag element whose key 
    is 'addr:street'.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    This function expands all street direction 
    abbreviations into the full, proper string:
        N, N., N* -> North
        S, S., S* -> South
        ...
    """
    
    mapping = {
        "N" : "North", "N." : "North", "N*" : "North", 
        "S" : "South", "S." : "South", "S*" : "South", 
        "E" : "East", "E." : "East", "E*" : "East", 
        "W" : "West", "W." : "West", "W*" : "West"
    }
    
    def update_direction(street_name):
        words = street_name.split(" ")
        
        if words[0] in mapping.keys():
            words[0] = mapping[words[0]]
        if words[-1] in mapping.keys() and words[-2] not in ["Suite", "Ste", "Ste."]:
            # update the direction only if the suffix 
            # does not follow the word or abbreviation 
            # for "Suite"
            words[-1] = mapping[words[-1]]
            
        words = " ".join(words)
        
        return words
    
    def is_street_name(elem):
        return (elem.attrib['k'] == "addr:street")
    
    for tag in element.iter("tag"):
        if is_street_name(tag):
            tag.attrib['v'] = update_direction(tag.attrib['v'])
    
    return element


def update_city(element):
    """
    Updates the city names for consistency and 
    correcting any misspellings for tags with 
    the 'addr:city' key based on mapping.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    """
    
    mapping = {
        "Manakin Sabot" : "Manakin-Sabot", 
        "Midolthian" : "Midlothian", 
        "Richmond City" : "Richmond", 
        "richmond" : "Richmond", 
        "glen Allen" : "Glen Allen"
    }
    
    def update_city_name(city):
        if city in mapping.keys():
            city = mapping[city]
        return city
    
    def is_city(elem):
        return (elem.attrib['k'] == "addr:city")
    
    for tag in element.iter("tag"):
        if is_city(tag):
            tag.attrib['v'] = update_city_name(tag.attrib['v'])
    
    return element


def update_state(element):
    """
    Updates the states for consistency for tags 
    with the 'addr:state', 'gnis:ST_alpha', or 
    'is_in:state_code' key based on mapping.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    """
    
    mapping = {
        "Virginia" : "VA", 
        "Va" : "VA", 
        "va" : "VA"
    }
    
    def update_state_name(state):
        if state in mapping.keys():
            state = mapping[state]
        return state
    
    def is_state(elem):
        return (elem.attrib['k'] in ["addr:state", "gnis:ST_alpha", "is_in:state_code"])
    
    for tag in element.iter("tag"):
        if is_state(tag):
            tag.attrib['v'] = update_state_name(tag.attrib['v'])
    
    return element


def state_include(element):
    """
    Sets a boolean flag to false for state 
    values that are not 'VA' for tags with 
    the 'addr:state', 'gnis:ST_alpha', or 
    'is_in:state_code' key.
    
    Input:    cElementTree element
    Returns:  a boolean value
    """
    
    flag = True
    
    def is_state(elem):
        return (elem.attrib['k'] in ["addr:state", "gnis:ST_alpha", "is_in:state_code"])
    
    for tag in element.iter("tag"):
        if is_state(tag) and tag.attrib['v'] != "VA":
            flag = False
    
    return flag


def add_county_name(element):
    """
    Adds a tag for the county name to the element 
    that contains a county number tag based on 
    mapping_names.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    If the element's tag key is 'gnis:county_id', 
    then a tag with key 'gnis:county_name' is created.
    
    If the element's tag key is 'gnis:County_num', 
    then a tag with key 'gnis:County' is created.
    """
    
    mapping_names = {
        "036" : "Charles City", 
        "041" : "Chesterfield", 
        "075" : "Goochland", 
        "085" : "Hanover", 
        "087" : "Henrico", 
        "095" : "James City", 
        "101" : "King William", 
        "127" : "New Kent", 
        "145" : "Powhatan", 
        "149" : "Prince George", 
        "159" : "Richmond", 
        "760" : "Richmond (city)"
    }
    
    def add_gnis_county_name(element, county_num, idx):
        element.insert(idx, ET.Element("tag", {'k':'gnis:county_name', 'v':mapping_names[county_num]}))
    
    def add_gnis_county(element, county_num, idx):
        element.insert(idx, ET.Element("tag", {'k':'gnis:County', 'v':mapping_names[county_num]}))
    
    def is_county_id(elem):
        return (elem.attrib['k'] == "gnis:county_id")
    
    def is_county_num(elem):
        return (elem.attrib['k'] == "gnis:County_num")
    
    idx = 0
    for tag in element.iter():
        if tag.tag == "tag":
            if is_county_id(tag):
                add_gnis_county_name(element, tag.attrib['v'], idx)
            if is_county_num(tag):
                add_gnis_county(element, tag.attrib['v'], idx)
        idx += 1
    
    return element


def add_county_number(element):
    """
    Adds a tag for the county number to the element 
    that contains a county name tag based on 
    mapping_names.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    If the element's tag key is 'gnis:county_name', 
    then a tag with key 'gnis:county_id' is created.
    
    If the element's tag key is 'gnis:County', 
    then a tag with key 'gnis:County_num' is created.
    """
    
    mapping_names = {
        "Charles City" : "036", 
        "Chesterfield" : "041", 
        "Goochland" : "075", 
        "Hanover" : "085", 
        "Henrico" : "087", 
        "James City" : "095", 
        "King William" : "101", 
        "New Kent" : "127", 
        "Powhatan" : "145", 
        "Prince George" : "149", 
        "Richmond" : "159", 
        "Richmond (city)" : "760"
    }
    
    def add_gnis_county_id(element, county_name, idx):
        element.insert(idx, ET.Element("tag", {'k':'gnis:county_id', 'v':mapping_names[county_name]}))
    
    def add_gnis_county_num(element, county_name, idx):
        element.insert(idx, ET.Element("tag", {'k':'gnis:County_num', 'v':mapping_names[county_name]}))
    
    def is_county_name(elem):
        return (elem.attrib['k'] == "gnis:county_name")
    
    def is_county(elem):
        return (elem.attrib['k'] == "gnis:County")
    
    idx = 0
    for tag in element.iter():
        if tag.tag == "tag":
            if is_county_name(tag):
                add_gnis_county_id(element, tag.attrib['v'], idx)
            if is_county(tag):
                add_gnis_county_num(element, tag.attrib['v'], idx)
        idx += 1
    
    return element


def update_country(element):
    """
    Updates the country for consistency for tags 
    with the 'addr:country', or 'is_in:country' 
    key based on mapping.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    """
    
    mapping = {
        "USA" : "US", 
        "United States" : "US", 
        "United States of America" : "US"
    }
    
    def update_country_name(country):
        if country in mapping.keys():
            country = mapping[country]
        return country
    
    def is_country(elem):
        return (elem.attrib['k'] in ["is_in:country", "addr:country"])
    
    for tag in element.iter("tag"):
        if is_country(tag):
            tag.attrib['v'] = update_country_name(tag.attrib['v'])
    
    return element


def country_include(element):
    """
    Sets a boolean flag to false for country 
    values that are not 'US' for tags with 
    the 'addr:country' or 'is_in:country' key.
    
    Input:    cElementTree element
    Returns:  a boolean value
    """
    
    flag = True
    
    def is_country(elem):
        return (elem.attrib['k'] in ["is_in:country", "addr:country"])
    
    for tag in element.iter("tag"):
        if is_country(tag) and tag.attrib['v'] != "US":
            flag = False
    
    return flag


def update_postal_code(element):
    """
    Updates the postal/zip code for consistency 
    for tags with a key within postal_code_keys 
    to the first 5 digits of the postal code value.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    Some postal codes may have the four-digit 
    suffix, however since the majority of the 
    postal codes only contain the five-digit 
    code, anything beyond the fifth digit in 
    the string is dropped.
    """
    
    def is_postal_code(elem):
        postal_code_keys = [
            "addr:postcode", "postal_code", "tiger:zip", 
            "tiger:zip_left", "tiger:zip_left_1", 
            "tiger:zip_left_2", "tiger:zip_left_3", 
            "tiger:zip_left_4", "tiger:zip_left_5", 
            "tiger:zip_right", "tiger:zip_right_1", 
            "tiger:zip_right_2", "tiger:zip_right_3"
        ]
        return (elem.attrib['k'] in postal_code_keys)
    
    for tag in element.iter("tag"):
        if is_postal_code(tag) and len(tag.attrib['v']) > 5:
            tag.attrib['v'] = tag.attrib['v'][:5]
    
    return element


def postal_code_include(element):
    """
    Sets a boolean flag to false for postal code 
    values that do not begin with one of a set of 
    three-digit codes for tags with the 'addr:postcode', 
    'postal_code', or 'tiger:zip' key.
    
    Input:    cElementTree element
    Returns:  a boolean value
    
    For this specific dataset, all postal/zip codes 
    to be included in the dataset should begin 
    with '230', '231', '232', or '238'.
    """
    
    flag = True
    
    def is_postal_code(elem):
        return (elem.attrib['k'] in ["addr:postcode", "postal_code", "tiger:zip"])
    
    for tag in element.iter("tag"):
        if is_postal_code(tag) and tag.attrib['v'][:3] not in ["230", "231", "232", "238"]:
            flag = False
    
    return flag


def update_max_speed(element):
    """
    Updates the max speed values for consistency 
    for tags with the 'maxspeed' or 'maxspeed:advisory' 
    key.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    
    Some max speed values only show the value while 
    the majority shows the value with the units. 
    For example, '30' becomes '30 mph'.
    """
    
    def update_speed(speed):
        words = speed.split(' ')
        words = ' '.join([words[0], "mph"])
        return words
    
    def is_max_speed(elem):
        return (elem.attrib['k'] in ["maxspeed", "maxspeed:advisory"])
    
    for tag in element.iter("tag"):
        if is_max_speed(tag):
            tag.attrib['v'] = update_speed(tag.attrib['v'])
    
    return element


def update_denomination(element):
    """
    Updates the denominations for consistency for 
    tags with the 'denomination' key based on mapping.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    """
    
    mapping = {
        "nondenominational" : "none", 
        "None" : "none", 
        "presbyterian_church_in_america" : "presbyterian", 
        "united_methodist" : "methodist"
    }
    
    def update_denom(denomination):
        if denomination in mapping.keys():
            denomination = mapping[denomination]
        return denomination
    
    def is_denomination(elem):
        return (elem.attrib['k'] == "denomination")
    
    for tag in element.iter("tag"):
        if is_denomination(tag):
            tag.attrib['v'] = update_denom(tag.attrib['v'])
    
    return element


def update_religion(element):
    """
    Updates the religions for consistency for 
    tags with the 'religion' key by returning 
    all lowercase strings as the value.
    
    Input:    cElementTree element
    Returns:  cElementTree element (updated)
    """
    
    def is_religion(elem):
        return (elem.attrib['k'] == "religion")
    
    for tag in element.iter("tag"):
        if is_religion(tag):
            tag.attrib['v'] = tag.attrib['v'].lower()
    
    return element


def clean_data(osm_file, clean_file):
    """
    Iterates through the elements of the osm_file, 
    cleans or excludes each element based on the 
    element's tags, then writes each cleaned element 
    to the clean_file in xml format.
    
    Input:    file name of the OSM data file (string)
    Returns:  file name of the cleaned data file (string)
    """
    
    def get_element(osm_file, tags=('node', 'way', 'relation')):
        context = iter(ET.iterparse(osm_file, events=('start', 'end')))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()
    
    print("Writing cleaned elements to clean file...")
    
    with open(clean_file, "wb") as output:
        output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write(b'<osm>\n  ')
        for i, element in enumerate(get_element(osm_file)):
            
            # cleans the street, street direction, city, and state tags
            element = update_state(update_city(update_street_direction(update_street(element))))
            # adds county name/number tags
            element = add_county_number(add_county_name(element))
            # cleans the country, postal/zip code, and max speed tags
            element = update_max_speed(update_postal_code(update_country(element)))
            # cleans the denomination and religion tags
            element = update_religion(update_denomination(element))
            
            if state_include(element) and country_include(element) and postal_code_include(element):
                # if the element passes the state, country, and postal code tests, 
                # then the element will be written to the clean_data file
                output.write(ET.tostring(element, encoding='utf-8'))
            
        output.write(b'</osm>')
    
    print("Cleaned file created.")
    
    return clean_file

